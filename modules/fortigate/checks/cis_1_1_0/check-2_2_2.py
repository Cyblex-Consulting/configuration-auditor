from core.checker import Checker

class Check_CIS_2_2_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.2.2"
        self.title = "Ensure administrator password retries and lockout time are configured"
        self.levels = [1]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_global = self.get_config("system global")

        if config_system_global is None:
            self.set_message(f'No \"config system global\" block defined')
            return False

        if "admin-lockout-threshold" not in config_system_global.keys():
            self.set_message(f'No admin-lockout-threshold configured')
            return False

        if not int(config_system_global["admin-lockout-threshold"]) > 0:
            self.set_message(f'Admin lockout threshold is set to {config_system_global["admin-lockout-threshold"]}')
            return False

        self.add_message(f'set admin-lockout-threshold {config_system_global["admin-lockout-threshold"]}')

        if "admin-lockout-duration" not in config_system_global.keys():
            self.set_message(f'No admin-lockout-duration configured')
            return False

        if not int(config_system_global["admin-lockout-duration"]) > 0:
            self.set_message(f'Admin lockout duration is set to {config_system_global["admin-lockout-duration"]}')
            return False

        self.add_message(f'set admin-lockout-duration {config_system_global["admin-lockout-duration"]}')

        return True

