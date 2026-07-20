from core.checker import Checker

class Check_CIS_3_3(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "3.3"
        self.title = "Ensure Policies are Uniquely Named"
        self.levels = [2]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_firewall_policy = self.get_config("firewall policy")

        if config_firewall_policy is None:
            self.set_message(f'No \"config firewall policy\" block defined')
            return False

        fail = False
        
        if len(config_firewall_policy['edits']) > 0:
            all_names = []
            for edit in config_firewall_policy['edits']:
                if not 'name' in edit.keys():
                    fail = True
                    self.add_message(f'The policy {edit["uuid"]} has no name')
                else:
                    if edit['name'] not in all_names:
                        all_names.append(edit['name'])
                    else:
                        fail = True
                        self.add_message(f'Policy {edit["name"]} exists multiple times')
        else:
            self.add_message('There is no policy defined')

        if not fail:
            self.add_message('All policies are named and have different names')

        return not fail
