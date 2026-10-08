from core.checker import Checker
from modules.pfsense.checks.cis_1_1_0 import _rules


class Check_Pfsense_4_1_5(Checker):
    """4.1.5 Ensure Logging is Enabled for All Firewall Rules."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "4.1.5"
        self.title = "Ensure Logging is Enable for All Firewall Rules"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        rules = [r for r in self.device.get_filter_rules() if isinstance(r, dict)]
        if not rules:
            self.set_message("No firewall rules found")
            return None

        without_logging = []
        for i, rule in enumerate(rules):
            if _rules.is_disabled(rule):
                continue
            if not _rules.has_logging(rule):
                without_logging.append(_rules.rule_label(rule, i))

        if without_logging:
            self.set_message("Rules without logging: " + ", ".join(without_logging))
            return False
        self.set_message("All enabled firewall rules have logging enabled")
        return True
