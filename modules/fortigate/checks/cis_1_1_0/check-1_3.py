from core.checker import Checker

class Check_CIS_1_3(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "1.3"
        self.title = "Disable all management related services on WAN port"
        self.levels = [1]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        wan_interfaces = self.firewall.get_wan_interfaces()

        fail = False
        for interface in wan_interfaces:
            name = interface["edit"]
            if "allowaccess" in interface.keys():
                allowaccess_list = interface["allowaccess"]
                for allowaccess in allowaccess_list:
                    if allowaccess in ["ping", "https", "ssh", "snmp", "http", "radius-acct"]:
                        self.add_message(f'{allowaccess} allowed for interface {name}')
                        fail = True

        return not fail
