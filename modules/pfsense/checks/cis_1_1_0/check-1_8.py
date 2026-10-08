from core.checker import Checker


class Check_Pfsense_1_8(Checker):
    """1.8 Ensure Web Management is Set to use HTTPS."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.8"
        self.title = "Ensure Web Management is Set to use HTTPS"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        protocol = self.get_config("system/webgui/protocol")
        if protocol is None:
            # Default protocol for the webConfigurator is HTTPS.
            self.set_message("webgui protocol not set; pfSense default is HTTPS")
            return True
        if protocol.lower() == "https":
            self.set_message("webConfigurator uses HTTPS")
            return True
        self.set_message(f'webConfigurator uses "{protocol}" instead of HTTPS')
        return False
