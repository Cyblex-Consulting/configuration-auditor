from core.checker import Checker


class Check_Pfsense_1_2(Checker):
    """1.2 Ensure AutoConfigBackup is enabled.

    AutoConfigBackup state is a service setting not reliably present in
    config.xml, so this is validated manually.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.2"
        self.title = "Ensure AutoConfigBackup is enabled"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("In the GUI navigate to Services > Auto Config Backup.")
        self.add_question_context("Verify 'Enable ACB' is checked.")
        return self.ask_if_correct("Is AutoConfigBackup enabled?")
