from core.checker import Checker

class Check_CIS_4_4_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.4.1"
        self.title = "Block high risk categories on Application Control"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        appcontrol_profiles = self.firewall.get_appcontrol_profiles()
        
        fail = False

        if len(appcontrol_profiles) == 0:
            self.add_message('No Application Control profile')
            return False
        
        required_categories_blocked = ["P2P", "Proxy"]
        
        for appcontrol_profile in appcontrol_profiles:
            profile_name = appcontrol_profile["edit"]
            self.add_message(f'Profile {profile_name}:')
            
            categories_blocked = []
            
            for rule in appcontrol_profile["configs"][0]["edits"]:
                
                # Default action seems to be "Block"
                if "action" in rule.keys():
                    action = rule["action"]
                else:
                    action = "block"
                    
                # Show all applications
                if 'application' in rule.keys():
                    for app_id in rule['application']:
                        app_name = self.firewall.fortiguard.application_name_from_id(app_id)
                        if app_name is not None:
                            self.add_message(f'- Application {app_name} defined in the profile with action {action}')
                        else:
                            self.add_message(f'- Unknown app with id {app_id} defined in the profile with action {action}')
                            
                # Show all categories
                if 'category' in rule.keys():
                    for category_id in rule['category']:
                        category_name = self.firewall.fortiguard.category_name_from_id(category_id)
                        if category_name is not None:
                            self.add_message(f'- Category {category_name} defined in the profile with action {action}')
                            if action == "block":
                                categories_blocked.append(category_id)
                        else:
                            self.add_message(f'- Unknown category with id {category_id} defined in the profile with action {action}')
                            
            # Verify if categories that should be blocked are indeed blocked
            for category_to_block in required_categories_blocked:
                if self.firewall.fortiguard.category_id_from_name(category_to_block) not in categories_blocked:
                    fail = True
                    self.add_message(f'- Category {category_to_block} not blocked in profile {profile_name}')
                           
        if not fail:
            self.add_message('All Application Control profiles block P2P and Proxy')
            
                           
        return not fail