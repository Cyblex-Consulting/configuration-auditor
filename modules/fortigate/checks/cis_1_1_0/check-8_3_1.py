from core.checker import Checker

class Check_CIS_8_3_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "8.3.1"
        self.title = "Centralized Logging and Reporting"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_log_fortianalyzer_setting = self.get_config("log fortianalyzer setting")
        
        # TODO: Only Fortianalyzer is considered, other siems should be compliant too
        if config_log_fortianalyzer_setting is None:
            self.add_message("No fortianalyzer configured for this host")
            return False
               
        if "status" not in config_log_fortianalyzer_setting.keys():
            self.add_message("status not defined")
            return False
        else:
            if config_log_fortianalyzer_setting["status"] != "enable":
                self.add_message(f'Fortianalyser log forwarding is not enabled')
                return False
                
        return True