from core.checker import Checker


class Check_Pfsense_1_5(Checker):
    """1.5 Ensure DNS server is configured."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.5"
        self.title = "Ensure DNS server is configured"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        dnsservers = self.device.get_list("system/dnsserver")
        # Empty strings can appear for empty <dnsserver></dnsserver> elements.
        configured = [d for d in dnsservers if isinstance(d, str) and d.strip()]
        if not configured:
            self.set_message("No DNS server configured under system/dnsserver")
            return False
        for dns in configured:
            if not self.is_ip(dns):
                self.set_message(f'{dns} is not a valid DNS server IP')
                return False
        self.set_message(f'DNS servers: {", ".join(configured)}')
        return True
