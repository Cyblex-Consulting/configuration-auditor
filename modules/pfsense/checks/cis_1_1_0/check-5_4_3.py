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
        openvpnservers = self.device.get_list("openvpn/openvpn-server")
        if not openvpnservers:
            self.set_message("No OpenVPN server configured under openvpn/openvpn-server")
            return True
    
        result = True
        for server in openvpnservers:
            self.set_message(f"OpenVPN configuration:")
            if not "tls" in server.keys() or not server["tls"]:
                self.add_message(f"- OpenVPN server '{server['vpnid']}': TLS disabled")
                result =  False
            else:
                self.add_message(f"- OpenVPN server '{server['vpnid']}': TLS enabled")

        return result