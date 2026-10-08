from core.checker import Checker


class Check_Pfsense_1_1(Checker):
    """1.1 Ensure SSH warning banner is configured.

    The banner is set in /etc/ssh/sshd_config, which is not part of config.xml,
    so this must be validated manually.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.1"
        self.title = "Ensure SSH warning banner is configured"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("In the CLI run: grep \"^Banner\" /etc/ssh/sshd_config")
        self.add_question_context("The output should contain a 'Banner' parameter.")
        return self.ask_if_correct("Is an SSH warning banner configured?")
