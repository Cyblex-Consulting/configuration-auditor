from core.checker import Checker


class Check_Pfsense_2_1(Checker):
    """2.1 Ensure Sessions Timeout is set to less than or equal to 10 Minutes."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "2.1"
        self.title = "Ensure Sessions Timeout is set to less than or equal to 10 Minutes"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        timeout = self.get_config("system/webgui/session_timeout")
        if timeout is None or timeout == "":
            self.set_message("Session timeout is not configured (defaults to 4 hours)")
            return False
        try:
            minutes = int(timeout)
        except ValueError:
            self.set_message(f'Session timeout value "{timeout}" is not a number')
            return False
        if minutes <= 10:
            self.set_message(f'Session timeout is {minutes} minutes')
            return True
        self.set_message(f'Session timeout is {minutes} minutes (should be <= 10)')
        return False
