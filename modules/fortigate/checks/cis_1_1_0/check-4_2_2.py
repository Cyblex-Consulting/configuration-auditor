from core.checker import Checker

class Check_CIS_4_2_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.2.2"
        self.title = "Apply Antivirus Security Profile to Policies"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        interfaces = self.firewall.get_interfaces()
        policies = self.firewall.get_policies(actions=["accept"])
        
        policies_fail = []
        policies_success = []
        for policy in policies:
            if "av-profile" not in policy.keys():
                if "name" in policy.keys():
                    policies_fail.append(policy["name"])
                else:
                    policies_fail.append(policy["uuid"])
            else:
                if "name" in policy.keys():
                    policies_success.append(policy["name"])
                else:
                    policies_success.append(policy["uuid"])
        
        # Display results
        self.add_message(f'{len(policies_success)} policies have an A/V profile')
        for policy in policies_success:
            self.add_message(f'- {policy}')
        self.add_message(f'{len(policies_fail)} policies have no A/V profile')
        for policy in policies_fail:
            self.add_message(f'- {policy}')
            
        return len(policies_fail) == 0