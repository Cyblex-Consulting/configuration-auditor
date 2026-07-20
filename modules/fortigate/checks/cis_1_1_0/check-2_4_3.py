from core.checker import Checker

class Check_CIS_2_4_3(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.4.3"
        self.title = "Ensure admin accounts with different privileges having their correct profiles assigned"
        self.levels = [1]
        self.auto = False
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_accprofile = self.get_config("system accprofile")

        if config_system_accprofile is None:
            self.add_message("No account profile seems to be configured so we consider failed.")
            self.add_message("However, manual review of the configuration shall be performed")
            return False

        # TODO Perform Check
        self.set_message("Not Implemented")
        return None
