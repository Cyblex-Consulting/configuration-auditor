from core.checker import Checker

class Check_CIS_2_1_7(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.1.7"
        self.title = "Disable USB Firmware and configuration installation"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_system_autoinstall = self.get_config("system auto-install")

        if config_system_autoinstall is None:
            self.set_message(f'No "config system autoinstall" bloc in configuration file')
            return False
        
        if "auto-install-config" not in config_system_autoinstall.keys():
            self.set_message(f'No auto-install-config key')
            return False

        if "auto-install-image" not in config_system_autoinstall.keys():
            self.set_message(f'No auto-install-image key')
            return False

        if not config_system_autoinstall["auto-install-config"] == "disable":
            self.set_message(f'Auto Install Config is not disabled')
            return False

        if not config_system_autoinstall["auto-install-image"] == "disable":
            self.set_message(f'Auto Install Image is not disabled')
            return False

        return True
