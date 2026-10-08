from core.checker import Checker


class Check_Pfsense_5_1_1(Checker):
    """5.1.1 Ensure SNMP traps receivers is set."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.1.1"
        self.title = "Ensure SNMP traps receivers is set"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        snmpd = self.get_config("snmpd")
        if not isinstance(snmpd, dict) or "trapenable" not in snmpd:
            self.set_message("SNMP traps are not enabled, so no trap receiver is set")
            return False
        trapserver = snmpd.get("trapserver")
        if trapserver and str(trapserver).strip():
            self.set_message(f'SNMP trap receiver: {trapserver}')
            return True
        self.set_message("SNMP traps enabled but no trap receiver (trapserver) set")
        return False
