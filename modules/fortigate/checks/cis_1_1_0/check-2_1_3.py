from core.checker import Checker

class Check_CIS_2_1_3(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.1.3"
        self.title = "Ensure timezone is properly configured"
        self.levels = [1]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_system_global = self.get_config("system global")

        if config_system_global is None:
            self.set_message(f'No "config system global" bloc in configuration file')
            return False
        
        if not "timezone" in config_system_global.keys():
            self.set_message("No timezone defined")
            return False

        timezone = config_system_global["timezone"]

        self.question_context = 'The configured timezone is ' + self.firewall.all_timezones[timezone]

        return self.ask_if_correct()