from core.checker import Checker

class Check_CIS_8_1_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "8.1.1"
        self.title = "Enable Event Logging"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_message('Not implemented')
        return None