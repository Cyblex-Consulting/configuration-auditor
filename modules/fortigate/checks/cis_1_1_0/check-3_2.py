from core.checker import Checker

class Check_CIS_3_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "3.2"
        self.title = "Ensure that policies do not use \"ALL\" as Service"
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

        fail = False
        
        if len(config_firewall_policy['edits']) > 0:
            for edit in config_firewall_policy['edits']:
                if "service" in edit.keys() and edit['service'] == 'ALL' and "action" in edit.keys():
                    # it seems that when a policy is blocking, there is no "action" key. Here we look
                    # only for policies that are not blocking and using service ALL
                    fail = True
                    self.add_message(f'The policy {edit["uuid"]} is not compliant:')
                    if "name" in edit.keys():
                        self.add_message(f'\tname: {edit["name"]}')
                    if "srcintf" in edit.keys():
                        self.add_message(f'\tsrcintf: {edit["srcintf"]}')
                    if "dstintf" in edit.keys():
                        self.add_message(f'\tdstintf: {edit["dstintf"]}')
                    if "srcaddr" in edit.keys():
                        self.add_message(f'\tsrcaddr: {edit["srcaddr"]}')
                    if "dstaddr" in edit.keys():
                        self.add_message(f'\tdstaddr: {edit["dstaddr"]}')
                    if "action" in edit.keys():
                        self.add_message(f'\taction: {edit["action"]}')
            fail = True
        else:
            self.add_message('There is no policy defined')

        if not fail:
            self.add_message('There is no policy with set service ALL')

        return not fail
