from core.checker import Checker

class Check_CIS_4_4_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.4.2"
        self.title = "Block applications running on non-default ports"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        appcontrol_profiles = self.firewall.get_appcontrol_profiles()
        
        fail = False

        if len(appcontrol_profiles) == 0:
            self.add_message('No Application Control profile')
            return False
            
        fail = False  
        for appcontrol_profile in appcontrol_profiles:
            profile_name = appcontrol_profile["edit"]
            
            if "enforce-default-app-port" not in appcontrol_profile.keys():
                self.add_message(f'Default application ports is not defined for profile {profile_name}')
                fail = True
            else:
                if appcontrol_profile["enforce-default-app-port"] != "enable":
                    self.add_message(f'Default application ports is not enabled for profile {profile_name}')
                    fail = True
                
        return not fail