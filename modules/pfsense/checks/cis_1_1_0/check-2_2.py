from core.checker import Checker


class Check_Pfsense_2_2(Checker):
    """2.2 Ensure LDAP or RADIUS server configured."""

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "2.2"
        self.title = "Ensure LDAP or RADIUS server configured"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        authservers = self.device.get_list("system/authserver")
        remote = []
        for server in authservers:
            if not isinstance(server, dict):
                continue
            srvtype = server.get("type", "")
            if srvtype in ("ldap", "radius"):
                remote.append(f'{server.get("name", "?")} ({srvtype})')
        if remote:
            self.set_message(f'Remote authentication servers: {", ".join(remote)}')
            return True
        self.set_message("No LDAP or RADIUS authentication server configured")
        return False
