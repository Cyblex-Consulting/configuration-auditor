from core.checker import Checker

class Check_CIS_2_2_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.2.1"
        self.title = "Ensure 'Password Policy' is enabled"
        self.levels = [1]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_system_passwordpolicy = self.get_config("system password-policy")

        if config_system_passwordpolicy is None:
            self.set_message(f'No \"config system password-policy\" block defined')
            return False

        if "status" not in config_system_passwordpolicy.keys():
            self.set_message(f'No status configured')
            return False

        if not config_system_passwordpolicy["status"] == 'enable':
            self.set_message(f'Status is not enabled')
            return False

        for key in config_system_passwordpolicy.keys():
            self.add_message(f'set {key} {config_system_passwordpolicy[key]}')

        return True