from core.checker import Checker


class Check_Pfsense_5_4_3(Checker):
    """5.4.3 Ensure that OpenVPN is configured to use TLS encryption."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.4.3"
        self.title = "Ensure that OpenVPN is configured to use TLS encryption for secure communications"
        self.levels = [2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("For each OpenVPN server (VPN > OpenVPN), under "
                                  "'Cryptographic Settings', verify TLS is enabled.")
        return self.ask_if_correct("Is OpenVPN configured to use TLS encryption?")
