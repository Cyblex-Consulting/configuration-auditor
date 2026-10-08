from core.checker import Checker


class Check_Pfsense_5_4_2(Checker):
    """5.4.2 Apply a Trusted Signed Certificate for VPN Portal.

    Whether the VPN portal certificate is signed by a trusted CA requires
    manual review.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.4.2"
        self.title = "Apply a Trusted Signed Certificate for VPN Portal"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        self.add_question_context("In the GUI navigate to System > Cert. Manager > CAs.")
        self.add_question_context("Verify the VPN portal uses a certificate signed by a trusted CA "
                                  "(not self-signed).")
        return self.ask_if_correct("Does the VPN portal use a trusted signed certificate?")
