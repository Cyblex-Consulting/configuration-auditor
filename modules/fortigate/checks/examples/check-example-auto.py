from core.checker import Checker

class Check_Example_Manual(Checker):

    def __init__(self, firewall, display, verbose=False):

        super().__init__(firewall, display, verbose)

        self.id = "1.1.2"
        self.title = "Example Auto Check"
        self.levels = [1, 2]
        self.auto = True
        self.enabled = False # Remove this line to enable
        self.benchmark_author = "Example Org."

    def do_check(self):
        config_system_dns = self.get_config("system dns")

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

        self.set_message(f'{config_system_dns["primary"]} {config_system_dns["secondary"]}')

        return True
