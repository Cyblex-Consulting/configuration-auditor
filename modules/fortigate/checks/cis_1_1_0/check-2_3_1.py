from core.checker import Checker

class Check_CIS_2_3_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.3.1"
        self.title = "Ensure SNMP agent is disabled "
        self.levels = [1]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_snmp_sysinfo = self.get_config("system snmp sysinfo")

        if config_system_snmp_sysinfo is None:
            self.set_message(f'No \"config system snmp sysinfo\" block defined')
            return False

        if "status" not in config_system_snmp_sysinfo.keys():
            self.set_message(f'No status configured')
            return False

        if not config_system_snmp_sysinfo["status"] == 'disable':
            self.set_message(f'Status is set to {config_system_snmp_sysinfo["status"]}')
            return False

        self.set_message(f'Status disabled')

        return True