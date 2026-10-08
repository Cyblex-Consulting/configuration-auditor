from core.checker import Checker
from modules.pfsense.checks.cis_1_1_0 import _rules


class Check_Pfsense_4_1_2(Checker):
    """4.1.2 Ensure no Allow Rule with Any in Source field.

    Note: pfSense ships default "allow any" rules on LAN interfaces to preserve
    connectivity; those may be a documented, accepted exception.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "4.1.2"
        self.title = "Ensure no Allow Rule with Any in Source field present in the Firewall Rules"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        offenders = []
        for i, rule in enumerate(self.device.get_filter_rules()):
            if not isinstance(rule, dict):
                continue
            if _rules.is_disabled(rule) or not _rules.is_pass(rule):
                continue
            if _rules.source_is_any(rule):
                offenders.append(_rules.rule_label(rule, i))

        if offenders:
            self.set_message("Pass rules with 'any' source: " + ", ".join(offenders))
            return False
        self.set_message("No pass rule uses 'any' as source")
        return True
