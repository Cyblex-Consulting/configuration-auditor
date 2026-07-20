from core.checker import Checker

class Check_CIS_2_1_5(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.1.5"
        self.title = "Ensure hostname is set"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_system_global = self.get_config("system global")

        if config_system_global is None:
            self.set_message(f'No "config system global" bloc in configuration file')
            return False
        
        if "hostname" not in config_system_global.keys():
            self.set_message("Hostname not configured")
            return False

        if config_system_global["hostname"].startswith("FortiGate"):
            self.set_message(f'Hostname seems to be default value: {config_system_global["hostname"]}')
            return False

        self.set_message(f'{config_system_global["hostname"]}')

        return True
