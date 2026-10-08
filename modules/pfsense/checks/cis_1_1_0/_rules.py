"""Shared helpers for interpreting pfSense firewall filter rules.

A parsed rule is a dict. Relevant keys:
  - type: "pass" | "block" | "reject"
  - disabled: present (empty string) when the rule is disabled
  - log: present when logging is enabled
  - source / destination: dict; "any" is expressed as an <any/> element, which
    parses to the key "any" being present
  - protocol: absent means any protocol; when present, ports live in
    source/destination as <port>
  - descr: human description

These helpers are intentionally defensive because config.xml shapes vary.
"""


def is_pass(rule):
    # pfSense defaults an omitted type to "pass".
    return rule.get("type", "pass") == "pass"


def is_disabled(rule):
    return "disabled" in rule


def has_logging(rule):
    return "log" in rule


def _endpoint_is_any(endpoint):
    if not isinstance(endpoint, dict):
        # A bare string endpoint is not "any".
        return False
    return "any" in endpoint


def source_is_any(rule):
    return _endpoint_is_any(rule.get("source"))


def destination_is_any(rule):
    return _endpoint_is_any(rule.get("destination"))


def service_is_any(rule):
    # "Any service" == no protocol restriction and no destination port.
    protocol = rule.get("protocol")
    if protocol not in (None, ""):
        return False
    dest = rule.get("destination")
    if isinstance(dest, dict) and dest.get("port"):
        return False
    return True


def rule_label(rule, index):
    descr = rule.get("descr")
    if isinstance(descr, str) and descr.strip():
        return f'#{index} "{descr.strip()}"'
    iface = rule.get("interface", "?")
    return f'#{index} (interface {iface})'
