from core.checker import Checker


class Check_Pfsense_3_2(Checker):
    """3.2 Ensure Login Protection Threshold is set to 30 or less.

    The Login Protection (sshguard) threshold is not represented in config.xml,
    so this is validated manually.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "3.2"
        self.title = "Ensure Login Protection Threshold is set to 30 or less"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("In the GUI navigate to System > Advanced.")
        self.add_question_context("Check the 'Login Protection' > 'Threshold' field is <= 30.")
        return self.ask_if_correct("Is the Login Protection Threshold set to 30 or less?")
