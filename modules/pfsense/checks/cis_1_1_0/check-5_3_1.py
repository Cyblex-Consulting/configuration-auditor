from core.checker import Checker


class Check_Pfsense_5_3_1(Checker):
    """5.3.1 Ensure 'DNSSEC' is Enabled on DNS Service.

    The DNS Resolver (unbound) enables DNSSEC when <unbound><dnssec/></unbound>
    is present.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.3.1"
        self.title = "Ensure 'DNSSEC' is Enable on DNS Service"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        # DNSSEC only applies when the DNS Resolver is enabled.
        if self.device.has_flag("unbound/dnssec"):
            self.set_message("DNSSEC is enabled on the DNS Resolver")
            return True
        if self.get_config("unbound") is None:
            self.set_message("DNS Resolver (unbound) is not configured")
            return False
        self.set_message("DNSSEC is not enabled on the DNS Resolver")
        return False
