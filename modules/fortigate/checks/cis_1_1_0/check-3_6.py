from core.checker import Checker

class Check_CIS_3_6(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "3.6"
        self.title = "Ensure logging is enabled on all firewall policies"
        self.levels = [1]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_firewall_policy = self.get_config("firewall policy")

        if config_firewall_policy is None:
            self.set_message(f'No \"config firewall policy\" block defined')
            return False

        found_no_logging_policy = False
        
        if len(config_firewall_policy['edits']) > 0:
            for edit in config_firewall_policy['edits']:
                if 'logtraffic' not in edit.keys():
                    found_no_logging_policy = True
                    if 'name' in edit.keys():
                        self.add_message(f'No logging for rule \"{edit["name"]}\"')
                    else:
                        self.add_message(f'No logging for rule {edit["uuid"]}')
                else:
                    if edit["logtraffic"] != "all":
                        found_no_logging_policy = True
                        if 'name' in edit.keys():
                            self.add_message(f'Logging is not \"all\" for rule \"{edit["name"]}\"')
                        else:
                            self.add_message(f'Logging is not \"all\" for rule {edit["uuid"]}')
        else:
            self.add_message('There is no policy defined')

        return not found_no_logging_policy
