from core.checker import Checker


class Check_Pfsense_5_1_2(Checker):
    """5.1.2 Ensure SNMP traps is enabled.

    pfSense enables SNMP traps when <snmpd><trapenable/></snmpd> is present.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.1.2"
        self.title = "Ensure SNMP traps is enabled"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        if self.device.has_flag("snmpd/trapenable"):
            self.set_message("SNMP traps are enabled")
            return True
        self.set_message("SNMP traps are not enabled")
        return False
