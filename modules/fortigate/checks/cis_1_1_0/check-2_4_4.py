from core.checker import Checker

class Check_CIS_2_4_4(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.4.4"
        self.title = "Ensure idle timeout time is configured"
        self.levels = [1]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_global = self.get_config("system global")

        if config_system_global is None:
            self.set_message(f'No \"config system global\" block defined')
            return False

        if "admintimeout" not in config_system_global.keys():
            self.set_message(f'No admintimeout configured')
            return False

        self.set_message(f'Admin timeout configured to {config_system_global["admintimeout"]} minutes')

        if int(config_system_global["admintimeout"]) > 15:
            self.add_message(f'Recommanded maximum value is 15 minutes.')
            return False

        return True
