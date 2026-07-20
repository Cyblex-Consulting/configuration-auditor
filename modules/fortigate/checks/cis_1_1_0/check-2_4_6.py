from core.checker import Checker

class Check_CIS_2_4_6(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.4.6"
        self.title = "Apply Local-in Policies"
        self.levels = [1]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_firewal_localinpolicy = self.get_config("firewall local-in-policy")

        if config_firewal_localinpolicy is None:
            self.add_message("No Local-in Policy seems to be configured so we consider failed.")
            self.add_message("However, manual review of the configuration shall be performed")
            return False

        # TODO Perform Check
        self.set_message("Not Implemented")
        return None
