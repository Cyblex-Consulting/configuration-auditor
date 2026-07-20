from core.checker import Checker

class Check_CIS_4_2_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "4.2.1"
        self.title = "Ensure Antivirus Definition Push Updates are Configured"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"
        
    def do_check(self):
        config_autoupdate_pushupdate = self.get_config("system autoupdate push-update")
        
        if config_autoupdate_pushupdate is None:
            self.set_message(f'No autopudate push-update block in configuration')
            return False

        if "status" not in config_autoupdate_pushupdate.keys():
            self.set_message(f'No status for autopudate push-update')
            return False

        if not config_autoupdate_pushupdate["status"] == "enable":
            self.add_message("Push updates are not enabled")
            return False
        else:
            self.add_message("Push updates are enabled")
            return True
