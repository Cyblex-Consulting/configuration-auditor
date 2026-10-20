"""Read-only pfSense filter-rule what-if simulator."""
import ipaddress
import re
from dataclasses import dataclass


@dataclass
class SimulationQuery:
    interface: str
    source: str
    source_port: str
    destination: str
    destination_port: str
    protocol: str


class PfsenseSimulator:
    """Evaluate pfSense filter rules in their configured order."""

    def __init__(self, device):
        self.device = device
        self.aliases = {}
        for alias in device.get_aliases():
            if isinstance(alias, dict) and alias.get("name"):
                self.aliases[str(alias["name"])] = alias

    def evaluate(self, query):
        evaluations = []
        for number, rule in enumerate(self.device.get_filter_rules(), 1):
            if isinstance(rule, dict):
                evaluations.append(self._evaluate_rule(number, rule, query))
        first_match = next((item for item in evaluations if item["matched"]), None)
        return {
            "decision": "pass" if first_match and first_match["action"] == "pass" else "block",
            "matched_policy": first_match,
            "evaluations": evaluations,
        }

    def _evaluate_rule(self, number, rule, query):
        result = {
            "order": number,
            "id": str(rule.get("id") or rule.get("tracker") or number),
            "name": str(rule.get("descr") or ""),
            "action": str(rule.get("type") or "pass").lower(),
            "matched": False,
            "interface_match": False,
            "status": "enabled",
            "reasons": [],
            "unsupported": [],
            "policy": rule,
        }
        if "disabled" in rule:
            result["status"] = "disabled"
            result["reasons"].append("disabled")
            return result

        interface_match = self._interface_match(rule.get("interface"), query.interface)
        result["interface_match"] = interface_match
        checks = [
            (interface_match,
             "interface matches", "interface does not match"),
            (self._endpoint_match(rule.get("source"), query.source,
                                  query.source_port, query.interface),
             "source and source port match", "source or source port does not match"),
            (self._endpoint_match(rule.get("destination"), query.destination,
                                  query.destination_port),
             "destination and destination port match",
             "destination or destination port does not match"),
            (self._protocol_match(rule.get("protocol"), query.protocol),
             "protocol matches", "protocol does not match"),
            (self._ipprotocol_match(rule.get("ipprotocol"), query.source,
                                    query.destination),
             "IP version matches", "IP version does not match"),
        ]
        for matched, positive, negative in checks:
            result["reasons"].append(positive if matched else negative)
            if not matched:
                return result

        ipprotocol = str(rule.get("ipprotocol") or "").lower()
        if ipprotocol and ipprotocol not in ("inet", "inet6", "any"):
            result["unsupported"].append("ipprotocol")
        result["matched"] = True
        return result

    @staticmethod
    def _as_list(value):
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    def _interface_match(self, configured, interface):
        if not configured or not interface:
            return True
        values = re.split(r"[,\s]+", str(configured).strip())
        return "any" in [x.lower() for x in values] or interface in values

    def _protocol_match(self, configured, requested):
        if not configured or str(configured).lower() in ("any", "ip"):
            return True
        if not requested or requested.lower() == "any":
            return True
        configured_values = re.split(r"[/,\s]+", str(configured).lower())
        return requested.lower() in configured_values

    @staticmethod
    def _ipprotocol_match(configured, source, destination):
        configured = str(configured or "").lower()
        if configured in ("", "any") or not source or not destination:
            return True
        try:
            source_version = ipaddress.ip_address(source).version
            destination_version = ipaddress.ip_address(destination).version
        except ValueError:
            return False
        if configured == "inet":
            return source_version == 4 and destination_version == 4
        if configured == "inet6":
            return source_version == 6 and destination_version == 6
        return True

    def _endpoint_match(self, endpoint, address, port, interface=None):
        if not endpoint or not isinstance(endpoint, dict):
            return True
        address_values = []
        if "any" in endpoint:
            address_match = True
        else:
            for key in ("address", "network"):
                address_values.extend(self._as_list(endpoint.get(key)))
            # An undefined query address cannot prove a match against a rule
            # that explicitly restricts the source or destination address.
            address_match = not address_values or (
                any(
                    (interface and str(value).lower() == interface.lower())
                    or (bool(address) and self._address_matches(str(value), address))
                    for value in address_values
                )
            )
        if "not" in endpoint:
            address_match = not address_match
            if address_values and not address:
                address_match = False

        rule_port = endpoint.get("port")
        if rule_port in (None, "", "any"):
            port_match = True
        else:
            port_match = self._port_matches(rule_port, port)
        return address_match and port_match

    def _address_matches(self, selector, address):
        if not address or selector.lower() in ("any", "*", "(self)"):
            return True
        try:
            target = ipaddress.ip_address(address)
        except ValueError:
            return False
        alias = self.aliases.get(selector)
        if alias:
            if str(alias.get("type", "")).lower() == "port":
                return False
            values = alias.get("address") or alias.get("content") or ""
            return any(self._literal_address_matches(str(value), target)
                       for value in self._as_list(values)
                       for value in re.split(r"[\s,]+", value) if value)
        return self._literal_address_matches(selector, target)

    @staticmethod
    def _literal_address_matches(value, target):
        try:
            if "/" in value:
                return target in ipaddress.ip_network(value, strict=False)
            return target == ipaddress.ip_address(value)
        except ValueError:
            return False

    def _port_matches(self, selector, port):
        if not port:
            # An undefined query port must not match a rule that explicitly
            # restricts the port.  Otherwise a broad what-if query could
            # incorrectly select a port-specific rule before a more relevant
            # rule without a port restriction.
            return False
        try:
            target = int(port)
        except ValueError:
            return False
        values = self._as_list(selector)
        expanded = []
        for value in values:
            alias = self.aliases.get(str(value))
            if alias:
                value = alias.get("address") or alias.get("content") or ""
            expanded.extend(re.split(r"[\s,]+", str(value)))
        for value in expanded:
            value = value.strip()
            if not value:
                continue
            try:
                if "-" in value:
                    low, high = (int(x) for x in value.split("-", 1))
                    if low <= target <= high:
                        return True
                elif int(value) == target:
                    return True
            except ValueError:
                continue
        return False
