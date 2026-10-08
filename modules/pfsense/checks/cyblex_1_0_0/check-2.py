from core.checker import Checker
import re

# Patterns that suggest a NAT rule is temporary, for debugging, or was left
# behind. pfSense has no "proxy policy" concept (unlike FortiGate), so the
# equivalent second policy set to scan is the NAT rules: port forwards
# (nat/rule) and 1:1 NAT (nat/onetoone).
REGEX = re.compile('TEMP|tmp|test|DBG|Debug|Open BAR', re.IGNORECASE)


class Check_Cyblex_2(Checker):
    """Check NAT rules that look temporary or debug."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "2"
        self.title = "Check NAT rules that looks temporary or debug"
        self.levels = [1]
        self.auto = False
        self.benchmark_version = "1.0.0"
        self.benchmark_author = "Cyblex"

    def do_check(self):
        nat_rules = []
        for kind, path in (("port-forward", "nat/rule"), ("1:1", "nat/onetoone")):
            for rule in self.device.get_list(path):
                if isinstance(rule, dict):
                    nat_rules.append((kind, rule))

        if not nat_rules:
            self.set_message("No NAT rules defined")
            return True

        suspicious_rules = []
        for i, (kind, rule) in enumerate(nat_rules):
            descr = rule.get("descr", "")
            if not isinstance(descr, str):
                descr = ""
            descr = descr.strip()

            if descr and REGEX.search(descr):
                iface = rule.get("interface", "?")
                suspicious_rules.append({
                    "label": f'#{i} {kind} (interface {iface})',
                    "descr": descr if descr else "<no description>",
                })

        if suspicious_rules:
            self.add_question_context("The following NAT rules have a suspicious description:")
            for rule in suspicious_rules:
                self.add_question_context(f'{rule["label"]}: {rule["descr"]}')
            return self.ask_if_correct()

        self.set_message("No NAT rule with suspicious description found")
        return True
