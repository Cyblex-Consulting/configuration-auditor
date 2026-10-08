from core.checker import Checker


class Check_Pfsense_5_4_1(Checker):
    """5.4.1 Ensure RADIUS or LDAP are being used for VPN Authentication.

    Which authentication backend each VPN uses requires manual review.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.4.1"
        self.title = "Ensure RADIUS or LDAP are being used for VPN Authentication"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("Review each VPN's 'Backend for authentication'.")
        self.add_question_context("It should be an LDAP or RADIUS server, not Local Database.")
        return self.ask_if_correct("Do VPNs authenticate via RADIUS or LDAP?")
