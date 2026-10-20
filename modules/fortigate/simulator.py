"""Read-only FortiGate policy what-if simulator.

The evaluator deliberately models the policy-selection portion of FortiGate
firewall processing. It does not attempt to emulate UTM inspection, routing,
VIP translation, schedules, or Internet Service Database lookups.
"""
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


class FortigateSimulator:
    """Evaluate a query against policies in their configured order."""

    def __init__(self, device):
        self.device = device
        self.addresses = self._index("firewall address")
        self.groups = self._index("firewall addrgrp")
        self.services = self._index("firewall service custom")
        self.service_groups = self._index("firewall service group")
        self.zones = self._zone_members()

    def evaluate(self, query):
        evaluations = []
        policies = self.device.get_policies()
        for number, policy in enumerate(policies, 1):
            evaluations.append(self._evaluate_policy(number, policy, query))

        first_match = next((item for item in evaluations if item["matched"]), None)
        if first_match is None:
            decision = "block"
            matched_policy = None
        else:
            decision = "pass" if first_match["action"] == "accept" else "block"
            matched_policy = first_match
        return {"decision": decision, "matched_policy": matched_policy, "evaluations": evaluations}

    def _evaluate_policy(self, number, policy, query):
        identity = str(policy.get("edit", number))
        name = policy.get("name") or policy.get("comments") or ""
        result = {
            "order": number,
            "id": identity,
            "name": name,
            "action": policy.get("action", "deny"),
            "matched": False,
            "status": "enabled",
            "reasons": [],
            "unsupported": [],
            "policy": policy,
        }
        if policy.get("status") == "disable":
            result["status"] = "disabled"
            result["reasons"].append("disabled")
            return result

        checks = [
            ("interface", self._interface_match(policy, query.interface),
             "interface matches", "interface does not match"),
            ("source", self._address_match(policy, "srcaddr", query.source),
             "source matches", "source does not match"),
            ("destination", self._address_match(policy, "dstaddr", query.destination),
             "destination matches", "destination does not match"),
            ("service", self._service_match(policy, query.protocol, query.destination_port),
             "protocol/port matches", "protocol/port does not match"),
        ]
        for _, matched, positive, negative in checks:
            if matched:
                result["reasons"].append(positive)
            else:
                result["reasons"].append(negative)
                return result

        for field in ("schedule", "internet-service", "internet-service-src"):
            if field in policy and field != "schedule":
                result["unsupported"].append(field)
        if query.source_port:
            result["unsupported"].append("source-port (not a normal FortiGate policy selector)")
        if policy.get("schedule") not in (None, "always"):
            result["unsupported"].append("schedule")
        result["matched"] = True
        return result

    def _index(self, chapter):
        config = self.device.get_config(chapter) or {}
        edits = config.get("edits", []) if isinstance(config, dict) else []
        return {str(item.get("edit")): item for item in edits if isinstance(item, dict) and item.get("edit")}

    def _zone_members(self):
        result = {}
        config = self.device.get_config("system zone") or {}
        for zone in config.get("edits", []) if isinstance(config, dict) else []:
            if not isinstance(zone, dict) or not zone.get("edit"):
                continue
            members = zone.get("interface", [])
            result[str(zone["edit"])] = set(self._as_list(members))
        return result

    @staticmethod
    def _as_list(value):
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    def _interface_match(self, policy, interface):
        # The interactive form uses one interface; it is treated as the source
        # interface, which is the common outbound what-if use case.
        configured = self._as_list(policy.get("srcintf", "all"))
        if any(str(item).lower() == "all" for item in configured):
            return True
        for item in configured:
            item = str(item)
            if item == interface:
                return True
            if interface in self.zones.get(item, set()):
                return True
        return False

    def _address_match(self, policy, field, value):
        if not value:
            return True
        configured = self._as_list(policy.get(field, "all"))
        matched = any(self._address_object_contains(str(item), value) for item in configured)
        if policy.get(field + "-negate") == "enable":
            return not matched
        return matched

    def _address_object_contains(self, name, value):
        if name.lower() in ("all", "any"):
            return True
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False
        return self._resolve_address(name, set(), address)

    def _resolve_address(self, name, seen, address):
        if name in seen:
            return False
        seen.add(name)
        if name in self.groups:
            return any(self._resolve_address(str(member), seen.copy(), address)
                       for member in self._as_list(self.groups[name].get("member")))
        item = self.addresses.get(name)
        if not item:
            # A literal object name is useful with configs that omit the
            # address-object dump, but never guess at opaque names.
            return self._ip_in_value(name, address)
        for key in ("subnet", "ip"):
            if key == "subnet" and isinstance(item.get(key), list) and len(item[key]) == 2:
                try:
                    if address in ipaddress.ip_network(
                            f"{item[key][0]}/{item[key][1]}", strict=False):
                        return True
                except ValueError:
                    pass
            for candidate in self._as_list(item.get(key)):
                if self._ip_in_value(str(candidate), address):
                    return True
        if item.get("start-ip") and item.get("end-ip"):
            try:
                return ipaddress.ip_address(item["start-ip"]) <= address <= ipaddress.ip_address(item["end-ip"])
            except ValueError:
                pass
        return False

    @staticmethod
    def _ip_in_value(value, address):
        value = value.strip()
        try:
            if "/" in value:
                return address in ipaddress.ip_network(value, strict=False)
            return address == ipaddress.ip_address(value)
        except ValueError:
            return False

    def _service_match(self, policy, protocol, port):
        protocol = (protocol or "any").strip().lower()
        port_number = None
        if port:
            try:
                port_number = int(port)
            except ValueError:
                return False
        services = self._as_list(policy.get("service", "ALL"))
        return any(self._resolve_service(str(service), set(), protocol, port_number)
                   for service in services)

    def _resolve_service(self, name, seen, protocol, port):
        if name.lower() in ("all", "any"):
            return True
        if name in seen:
            return False
        seen.add(name)
        if name in self.service_groups:
            return any(self._resolve_service(str(member), seen.copy(), protocol, port)
                       for member in self._as_list(self.service_groups[name].get("member")))
        service = self.services.get(name)
        if not service:
            # Common hand-created service names such as TCP-8443 can still be
            # evaluated when the custom-service section is absent.
            service = {"edit": name}
        service_protocol = str(service.get("protocol", "")).lower()
        if service_protocol and service_protocol not in ("ip", "all", protocol):
            if not (service_protocol == "icmp" and protocol == "icmp"):
                return False
        if service_protocol in ("icmp", "ip", "all") and not service.get("tcp-portrange") and not service.get("udp-portrange"):
            return protocol in ("any", service_protocol) or service_protocol == "ip"
        keys = []
        if protocol in ("any", "tcp"):
            keys.append("tcp-portrange")
        if protocol in ("any", "udp"):
            keys.append("udp-portrange")
        if protocol == "sctp":
            keys.append("sctp-portrange")
        for key in keys:
            for value in self._as_list(service.get(key)):
                if port is None or self._port_in_range(str(value), port):
                    return True
        return False

    @staticmethod
    def _port_in_range(value, port):
        for part in re.split(r"[, ]+", value.replace(":", "-").strip()):
            if not part:
                continue
            try:
                if "-" in part:
                    low, high = (int(x) for x in part.split("-", 1))
                    if low <= port <= high:
                        return True
                elif int(part) == port:
                    return True
            except ValueError:
                continue
        return False
