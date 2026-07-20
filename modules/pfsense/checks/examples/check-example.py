from core.checker import Checker


class Check_Pfsense_Example(Checker):
    """Placeholder example check for the pfSense module (SKELETON).

    Disabled by default. It shows the shape a pfSense check should take.
    Implement PfsenseDevice.get_config() and real checks to make this useful.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "0.0.0"
        self.title = "pfSense Example Check (skeleton)"
        self.levels = [1, 2]
        self.auto = True
        self.enabled = False  # Remove this line to enable
        self.benchmark_version = "v0.0.0"
        self.benchmark_author = "Example Org."

    def do_check(self):
        # TODO: read configuration via self.get_config(...) and return
        # True (pass) / False (fail) / None (skip).
        return None
