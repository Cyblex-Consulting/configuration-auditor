from core.checker import Checker


class Check_Pfsense_5_1_3(Checker):
    """5.1.3 Ensure that the add-on package NET-SNMP is installed and configured securely.

    Package installation and SNMPv3 hardening require manual verification.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.1.3"
        self.title = "Ensure that the add-on package NET-SNMP is installed and configured securely"
        self.levels = [2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("If SNMP is used, verify the NET-SNMP package is installed and:")
        self.add_question_context("- SNMPv3 with strong auth/encryption is enabled")
        self.add_question_context("- SNMP access is restricted to authorized hosts")
        self.add_question_context("- default community strings are removed/changed")
        return self.ask_if_correct("Is NET-SNMP installed and configured securely (or SNMP unused)?")
