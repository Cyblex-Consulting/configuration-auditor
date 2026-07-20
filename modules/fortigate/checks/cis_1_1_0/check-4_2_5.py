from core.checker import Checker

class Check_CIS_4_2_5(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.2.5"
        self.title = "Enable grayware detection on antivirus"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_antivirus_settings = self.get_config("antivirus settings")
        
        if config_antivirus_settings is None:
            self.add_message('No "antivirus settings" block defined')
            return False

        if "grayware" not in config_antivirus_settings.keys():
            self.add_message('"grayware" not configured in "antivirus settings"')
            return False
        
        if config_antivirus_settings["grayware"] != "enable":
            self.add_message('"grayware" not enabled in "antivirus settings"')
            return False
                           
        return True