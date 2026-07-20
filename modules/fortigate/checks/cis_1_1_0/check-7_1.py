from core.checker import Checker

class Check_CIS_7_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "7.1"
        self.title = "Configuring the maximum login attempts and lockout period"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_user_settings= self.get_config("user settings")
        
        if config_user_settings is None:
            self.add_message("No user settings configured for this host")
            return False
        
        fail = False
        
        if "auth-lockout-threshold" not in config_user_settings.keys():
            self.add_message("auth-lockout-threshold not defined")
            fail = True
        else:
            auth_lockout_threshold = int(config_user_settings["auth-lockout-threshold"])
            if auth_lockout_threshold > 5:
                self.add_message(f'Authentication lockout threshold is configured to {auth_lockout_threshold} failed attempts which is higher that the recommanded value: 5')
                fail = True
                
        if "auth-lockout-duration" not in config_user_settings.keys():
            self.add_message("auth-lockout-duration not defined")
            fail = True
        else:
            auth_lockout_duration = int(config_user_settings["auth-lockout-duration"])
            if auth_lockout_duration < 300:
                self.add_message(f'Authentication lockout duration is configured to {auth_lockout_duration}s is lower that the recommanded value: 300')
                fail = True
                
        return not fail