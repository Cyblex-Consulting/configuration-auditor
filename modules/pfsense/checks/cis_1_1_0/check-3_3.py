from core.checker import Checker


class Check_Pfsense_3_3(Checker):
    """3.3 Ensure Allow access again after time is set to 300 or more seconds.

    The Login Protection blocktime is not represented in config.xml, so this is
    validated manually.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "3.3"
        self.title = "Ensure Allow access again after time is set to 300 or more seconds"
        self.levels = [2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("In the GUI navigate to System > Advanced > Admin Access.")
        self.add_question_context("Check the 'Login Protection' 'Blocktime' value is >= 300 seconds.")
        return self.ask_if_correct("Is the Blocktime set to 300 seconds or more?")
