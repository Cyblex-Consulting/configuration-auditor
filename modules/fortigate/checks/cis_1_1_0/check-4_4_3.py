from core.checker import Checker

class Check_CIS_4_4_3(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.4.3"
        self.title = "Ensure all Application Control related traffic are logged"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_message('Not implemented')
        return None