from core.checker import Checker
from modules.pfsense.checks.cis_1_1_0 import _rules


class Check_Pfsense_4_1_4(Checker):
    """4.1.4 Ensure there are no Unused Policies.

    Whether a rule is genuinely "unused" requires operational knowledge, so
    this is a manual check. Disabled rules are surfaced as candidates.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "4.1.4"
        self.title = "Ensure there are no Unused Policies"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        disabled = []
        for i, rule in enumerate(self.device.get_filter_rules()):
            if isinstance(rule, dict) and _rules.is_disabled(rule):
                disabled.append(_rules.rule_label(rule, i))

        if disabled:
            self.add_question_context("Disabled rules (candidates for removal):")
            for d in disabled:
                self.add_question_context(f'- {d}')
        else:
            self.add_question_context("No disabled rules found.")
        self.add_question_context("Review all firewall rules and confirm none are unused.")
        return self.ask_if_correct("Are there no unused firewall policies?")
