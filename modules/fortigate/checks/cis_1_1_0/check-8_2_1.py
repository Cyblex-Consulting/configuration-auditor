from core.checker import Checker

class Check_CIS_8_2_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "8.2.1"
        self.title = "Encrypt Log Transmission to FortiAnalyzer / FortiManager"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_log_fortianalyzer_setting = self.get_config("log fortianalyzer setting")
        
        if config_log_fortianalyzer_setting is None:
            self.add_message("No fortianalyzer configured for this host")
            return False
                
        if "enc-algorithm" not in config_log_fortianalyzer_setting.keys():
            self.add_message("enc-algorithm not defined")
            return False
        else:
            if config_log_fortianalyzer_setting["enc-algorithm"] != "high":
                self.add_message(f'High encryption algorithms is not defined')
                return False
                
        return True