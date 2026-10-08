from core.checker import Checker


class Check_Pfsense_5_2_1(Checker):
    """5.2.1 Ensure time zone is properly configured."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.2.1"
        self.title = "Ensure time zone is properly configured"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        timezone = self.get_config("system/timezone")
        if not timezone or not timezone.strip():
            self.set_message("No timezone configured (defaults to Etc/UTC)")
            return False
        self.set_message(f'Timezone is "{timezone}"')
        return True
