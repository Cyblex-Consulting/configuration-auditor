from core.checker import Checker

class Check_CIS_2_4_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.4.1"
        self.title = "Ensure default 'admin' password is changed"
        self.levels = [1]
        self.auto = False
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_admin = self.get_config("system admin")

        if config_system_admin is None:
            self.set_message(f'No \"config system admin\" block defined')
            return False

        if len(config_system_admin['edits']) > 0:
            for edit in config_system_admin['edits']:
                username = edit["edit"]
                if username == "admin":
                    username_admin_exists = True

        if username_admin_exists:
            return self.ask_if_correct('"admin" user exists. Is the default password changed?')
        else:
            self.set_message('User "admin" does not exist so this requirement is not really applicable. Considering PASS')
            return True