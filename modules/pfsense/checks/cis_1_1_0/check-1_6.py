from core.checker import Checker


class Check_Pfsense_1_6(Checker):
    """1.6 Ensure IPv6 is disabled if not used.

    pfSense allows IPv6 traffic when <system><ipv6allow/></system> is present.
    This check reports FAIL if IPv6 is allowed so the operator can confirm it
    is actually required. If IPv6 is in use, this may be intentionally waived.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.6"
        self.title = "Ensure IPv6 is disabled if not used"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        if self.device.has_flag("system/ipv6allow"):
            self.set_message("IPv6 is allowed (system/ipv6allow present). "
                             "Disable it if IPv6 is not used.")
            return False
        self.set_message("IPv6 is not allowed")
        return True
