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
        enabled = self.device.has_flag("snmpd/enable")

        if not enabled:
            self.set_message("SNMP is not enabled")
            return True
        else:
            self.set_message("SNMP is enabled")

        ro_community = self.get_config("snmpd/rocommunity")
        rw_community = self.get_config("snmpd/rwcommunity")

        self.add_question_context("Verify the NET-SNMP package is installed and:")
        self.add_question_context("- SNMPv3 with strong auth/encryption is enabled")
        self.add_question_context("- SNMP access is restricted to authorized hosts")
        self.add_question_context("- Community strings are not trivial")
        if enabled and ro_community:
            self.add_question_context(f"  + RO Community : {ro_community}")
        if enabled and rw_community:
            self.add_question_context(f"  + RW Community : {rw_community}")
        return self.ask_if_correct("Is NET-SNMP installed and configured securely?")
