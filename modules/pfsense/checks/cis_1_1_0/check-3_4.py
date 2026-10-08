from core.checker import Checker


class Check_Pfsense_3_4(Checker):
    """3.4 Ensure default password of admin is changed.

    Password hashes are not exposed for comparison here, so this is validated
    manually (try logging in with admin/pfsense).
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "3.4"
        self.title = "Ensure default password of admin is changed"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("Try to log in to the GUI with admin / pfsense.")
        self.add_question_context("The default password must NOT work.")
        return self.ask_if_correct("Has the default 'admin' password been changed?")
