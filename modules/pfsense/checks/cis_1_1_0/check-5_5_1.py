from core.checker import Checker


class Check_Pfsense_5_5_1(Checker):
    """5.5.1 Ensure that OpenVPN use strong ciphers or hashing algorithms.

    Cipher/hash strength assessment is left to the operator; any OpenVPN server
    cipher settings found are surfaced for review.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "5.5.1"
        self.title = "Ensure that OpenVPN use strong ciphers or hashing algorithms"
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
            self.set_message(f"OpenVPN server '{server['vpnid']}' configuration:")
            if not "tls" in server.keys() or not server["tls"]:
                self.add_message(f" TLS disabled")
                result =  False

            dh_length = server.get("dh_length", None)
            if dh_length is None or int(dh_length) < 2048:
                self.add_message(f" DH length:{dh_length} is less than 2048")
                result =  False
            else:
                self.add_message(f" DH length: {dh_length} is acceptable")

            digest = server.get("digest", None)
            if digest is None or digest.lower() not in ["sha256", "sha384", "sha512"]:
                self.add_message(f" Digest: {digest} is not a secure hash algorithm")
                result =  False
            else:
                self.add_message(f" Digest: {digest} is acceptable")

            data_ciphers = server.get("data_ciphers", None)
            if data_ciphers is None:
                self.add_message(f" No data cipher configured")
                result =  False
            else:
                for data_cipher in data_ciphers.split(","):
                    if data_cipher.lower() not in ["aes-128-gcm","aes-256-gcm", "chacha20-poly1305"]:
                        self.add_message(f" Data cipher: {data_cipher} is not a secure cipher")
                        result =  False
                    else:
                        self.add_message(f" Data cipher: {data_cipher} is acceptable")

        return result