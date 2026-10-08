from core.checker import Checker


class Check_Pfsense_2_3(Checker):
    """2.3 Ensure Console Menu is Password Protected.

    pfSense protects the console menu when
    <system><disableconsolemenu/></system> is present.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "2.3"
        self.title = "Ensure Console Menu is Password Protected"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        if self.device.has_flag("system/disableconsolemenu"):
            self.set_message("Console menu is password protected (disableconsolemenu present)")
            return True
        self.set_message("Console menu is NOT password protected")
        return False
