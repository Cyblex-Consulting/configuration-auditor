from core.checker import Checker

class Check_CIS_1_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "1.1"
        self.title = "Ensure DNS server is configured"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"
        
    def do_check(self):
        config_system_dns = self.get_config("system dns")

        if config_system_dns is None:
            self.set_message(f'No "config system dns" bloc in configuration file')
            return False

        if "primary" not in config_system_dns.keys():
            self.set_message(f'No primary DNS configured')
            return False

        if not self.is_ip(config_system_dns["primary"]):
            self.set_message(f'{config_system_dns["primary"]} is not a valid IP for primary DNS')
            return False

        if "secondary" not in config_system_dns.keys():
            self.set_message(f'No secondary DNS configured')
            return False

        if not self.is_ip(config_system_dns["secondary"]):
            self.set_message(f'{config_system_dns["secondary"]} is not a valid IP for secondary DNS')
            return False

        self.add_message(f'{config_system_dns["primary"]}')
        self.add_message(f'{config_system_dns["secondary"]}')

        return True
