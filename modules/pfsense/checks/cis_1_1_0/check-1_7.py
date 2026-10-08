from core.checker import Checker


class Check_Pfsense_1_7(Checker):
    """1.7 Ensure 'DNS Rebind Check' is enabled.

    pfSense disables the DNS rebind protection when
    <system><webgui><nodnsrebindcheck/></webgui></system> is present. The
    protection should stay enabled, i.e. that flag should be absent.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.7"
        self.title = "Ensure 'DNS Rebind Check' is enabled"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        if self.device.has_flag("system/webgui/nodnsrebindcheck"):
            self.set_message("DNS Rebind Check is DISABLED (nodnsrebindcheck present)")
            return False
        self.set_message("DNS Rebind Check is enabled")
        return True
