from core.checker import Checker


class Check_Pfsense_1_2(Checker):
    """1.2 Ensure AutoConfigBackup is enabled.

    AutoConfigBackup state is a service setting not reliably present in
    config.xml, so this is validated manually.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.2"
        self.title = "Ensure AutoConfigBackup is enabled"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        enabled = self.get_config("system/acb/enable")
        if not enabled:
            self.set_message("AutoConfigBackup is not enabled")
            return False
        self.set_message("AutoConfigBackup is enabled")
        return True