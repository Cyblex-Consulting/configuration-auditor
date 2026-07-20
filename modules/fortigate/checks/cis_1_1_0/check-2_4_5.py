from core.checker import Checker

class Check_CIS_2_4_5(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.4.5"
        self.title = "Ensure only encrypted access channels are enabled"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        interfaces = self.firewall.get_interfaces()

        fail = False
        for interface in interfaces:
            name = interface["edit"]
            if "allowaccess" in interface.keys():
                allowaccess = interface["allowaccess"]
                if not isinstance(allowaccess, list):
                    allowaccess = [allowaccess]
                if "http" in allowaccess or "telnet" in allowaccess:
                    fail = True
                self.add_message(f'{name}: set allowaccess {" ".join(allowaccess)}')
        
        return not fail
