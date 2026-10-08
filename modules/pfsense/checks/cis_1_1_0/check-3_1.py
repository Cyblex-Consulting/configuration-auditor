from core.checker import Checker


class Check_Pfsense_3_1(Checker):
    """3.1 Ensure 'Local Account status' is set to 'Disabled'.

    Every local user except 'admin' should be disabled (a disabled pfSense user
    has an empty <disabled></disabled> element). The 'admin' account must stay
    enabled for HA synchronization.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "3.1"
        self.title = "Ensure 'Local Account status' is set to 'Disabled'"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        users = self.device.get_users()
        enabled_local = []
        for user in users:
            if not isinstance(user, dict):
                continue
            name = user.get("name", "")
            if name == "admin":
                continue
            if "disabled" not in user:
                enabled_local.append(name)

        if enabled_local:
            self.set_message("Enabled local accounts (should be disabled): "
                             + ", ".join(enabled_local))
            return False
        self.set_message("All local accounts other than 'admin' are disabled")
        return True
