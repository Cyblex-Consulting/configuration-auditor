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
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):

        openvpnservers = self.device.get_list("openvpn/openvpn-server")
        if not openvpnservers:
            self.set_message("No OpenVPN server configured under openvpn/openvpn-server")
            return True

        result = True
        for server in openvpnservers:
            authmode = server["authmode"]
            if authmode not in ["LDAP", "RADIUS"]:
                result = False
            self.set_message(f"OpenVPN server '{server['vpnid']}' uses authentication backend: {authmode}")

        return result
