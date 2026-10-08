from core.checker import Checker


class Check_Pfsense_1_3(Checker):
    """1.3 Ensure 'Message Of The Day (MOTD)' is set.

    The MOTD lives in /etc/motd, not config.xml, so this is validated manually.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.3"
        self.title = "Ensure 'Message Of The Day (MOTD)' is set"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("In the pfSense shell run: cat /etc/motd")
        self.add_question_context("Verify a custom Message Of The Day is set "
                                  "(not the default FreeBSD banner).")
        return self.ask_if_correct("Is a custom MOTD set?")
