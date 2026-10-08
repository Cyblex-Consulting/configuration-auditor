from core.checker import Checker


class Check_Pfsense_1_4(Checker):
    """1.4 Ensure Hostname is set."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.4"
        self.title = "Ensure Hostname is set"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        hostname = self.get_config("system/hostname")
        if not hostname:
            self.set_message("No hostname configured")
            return False
        if hostname == "pfSense":
            self.set_message("Hostname is still the default 'pfSense'")
            return False
        self.set_message(f'Hostname is "{hostname}"')
        return True
