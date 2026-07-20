from core.checker import Checker

class Check_CIS_2_3_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.3.2"
        self.title = "Ensure only SNMPv3 is enabled"
        self.levels = [2]
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

        if not config_system_snmp_sysinfo["status"] == 'enable':
            self.set_message(f'SNMP agent status is set to {config_system_snmp_sysinfo["status"]}')
            self.add_message(f'2.3.2 is therefore not applicable, we consider it PASS')
            return True

        fail = False
        # Check if a community is set
        config_system_snmp_community = self.get_config("system snmp community")

        if len(config_system_snmp_community['edits']) > 0:
            self.set_message('There are SNMP communities defined:')
            for edit in config_system_snmp_community['edits']:
                self.add_message(f'name: {edit["name"]}')
            fail = True
        else:
            self.add_message('There are no SNMP community defined')

        # Check the SNMPv3 users configured
        config_system_snmp_user = self.get_config("system snmp user")

        if len(config_system_snmp_user['edits']) > 0:
            self.add_message('There are SNMP users defined:')
            for edit in config_system_snmp_user['edits']:
                self.add_message(f'user: {edit["edit"]}')
        else:
            self.add_message('There are no SNMP users defined')

        return not fail