from core.checker import Checker
import re

# Patterns that suggest a rule is temporary, for debugging, or overly permissive
# and was left behind. Same intent as the FortiGate Cyblex check.
REGEX = re.compile('TEMP|tmp|test|DBG|Debug|Open BAR', re.IGNORECASE)


class Check_Cyblex_1(Checker):
    """Check firewall rules that look temporary or debug."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1"
        self.title = "Check firewall rules that looks temporary or debug"
        self.levels = [1]
        self.auto = False
        self.benchmark_version = "1.0.0"
        self.benchmark_author = "Cyblex"

    def do_check(self):
        rules = self.device.get_filter_rules()

        if not rules:
            self.set_message("No firewall rules defined")
            return True

        suspicious_rules = []
        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                continue

            descr = rule.get("descr", "")
            if not isinstance(descr, str):
                descr = ""
            descr = descr.strip()

            if descr and REGEX.search(descr):
                iface = rule.get("interface", "?")
                suspicious_rules.append({
                    "label": f'#{i} (interface {iface})',
                    "descr": descr if descr else "<no description>",
                })

        if suspicious_rules:
            self.add_question_context("The following firewall rules have a suspicious description:")
            for rule in suspicious_rules:
                self.add_question_context(f'{rule["label"]}: {rule["descr"]}')
            return self.ask_if_correct()

        self.set_message("No firewall rule with suspicious description found")
        return True
