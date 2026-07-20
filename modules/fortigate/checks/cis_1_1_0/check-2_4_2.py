from core.checker import Checker

class Check_CIS_2_4_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.4.2"
        self.title = "Ensure all the login accounts having specific trusted hosts enabled"
        self.levels = [1]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_admin = self.get_config("system admin")

        if config_system_admin is None:
            self.set_message(f'No \"config system admin\" block defined')
            return False

        fail = False
        if len(config_system_admin['edits']) > 0:
            self.add_message('There are admin users defined:')
            for edit in config_system_admin['edits']:
                username = edit["edit"]
                self.add_message(f'user: {username}')
                there_is_trusthost = False
                for key in edit.keys():
                    if key.startswith('trusthost'):
                        there_is_trusthost = True
                        l = ' '.join(edit[key])
                        self.add_message(f'set {key} {l}')
                if not there_is_trusthost:
                    self.add_message("This account has no trusthost")
                    fail = True
        else:
            self.set_message('There are no user defined')
            return False

        return not fail
