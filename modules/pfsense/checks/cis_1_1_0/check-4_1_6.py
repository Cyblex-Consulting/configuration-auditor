from core.checker import Checker
from modules.pfsense.checks.cis_1_1_0 import _rules


class Check_Pfsense_4_1_6(Checker):
    """4.1.6 Ensure ICMP Request is securely configured.

    Whether the allowed ICMP types are appropriate needs operator judgement, so
    this is a manual check. Pass rules allowing ICMP are surfaced.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "4.1.6"
        self.title = "Ensure ICMP Request is securely configured"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        icmp_rules = []
        for i, rule in enumerate(self.device.get_filter_rules()):
            if not isinstance(rule, dict):
                continue
            if rule.get("protocol") == "icmp":
                icmptype = rule.get("icmptype", "any")
                icmp_rules.append(f'{_rules.rule_label(rule, i)} icmptype={icmptype}')

        if icmp_rules:
            self.add_question_context("ICMP rules found:")
            for r in icmp_rules:
                self.add_question_context(f'- {r}')
        else:
            self.add_question_context("No explicit ICMP rules found.")
        self.add_question_context("Confirm only necessary ICMP types are allowed.")
        return self.ask_if_correct("Is ICMP securely configured?")
