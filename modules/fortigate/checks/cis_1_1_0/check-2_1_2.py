from core.checker import Checker

class Check_CIS_2_1_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.1.2"
        self.title = "Ensure 'Post-Login Banner' is set"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_system_global = self.get_config("system global")
        
        if config_system_global is None:
            self.set_message(f'No "config system global" bloc in configuration file')
            return False
        
        if "post-login-banner" not in config_system_global.keys():
            self.set_message(f'Post-login banner not configured')
            return False

        if not config_system_global["post-login-banner"] == "enable":
            self.set_message(f'Post-login banner not enabled')
            return False

        return True
