from core.checker import Checker


class Check_Pfsense_6_1(Checker):
    """6.1 Ensure syslog is configured.

    pfSense enables remote logging when <syslog><enable/></syslog> is present
    and at least one remote server (remoteserver/remoteserver2/remoteserver3)
    is set.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "6.1"
        self.title = "Ensure syslog is configured"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        syslog = self.get_config("syslog")
        if not isinstance(syslog, dict):
            self.set_message("No syslog configuration present")
            return False
        if "enable" not in syslog:
            self.set_message("Remote logging is not enabled")
            return False

        servers = []
        for key in ("remoteserver", "remoteserver2", "remoteserver3"):
            value = syslog.get(key)
            if value and str(value).strip():
                servers.append(str(value).strip())

        if servers:
            self.set_message("Remote syslog servers: " + ", ".join(servers))
            return True
        self.set_message("Remote logging enabled but no remote server configured")
        return False
