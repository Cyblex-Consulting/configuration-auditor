from core.checker import Checker


class Check_Pfsense_1_9(Checker):
    """1.9 Ensure a synchronized High Availability peer is configured."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.9"
        self.title = "Ensure a synchronized High Availability peer is configured"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        sync_ip = self.get_config("hasync/synchronizetoip")
        if sync_ip and sync_ip.strip():
            self.set_message(f'HA peer synchronize-to IP: {sync_ip}')
            return True
        self.set_message("No High Availability peer configured (hasync/synchronizetoip empty)")
        return False
