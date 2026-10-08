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
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        servers = self.device.get_list("openvpn/openvpn-server")
        found = False
        for server in servers:
            if not isinstance(server, dict):
                continue
            found = True
            descr = server.get("description", server.get("vpnid", "?"))
            ciphers = server.get("data_ciphers", server.get("crypto", "?"))
            digest = server.get("digest", "?")
            self.add_question_context(f'OpenVPN server "{descr}": ciphers={ciphers}, digest={digest}')
        if not found:
            self.add_question_context("No OpenVPN server configuration found.")
        self.add_question_context("Confirm only strong ciphers/hashing algorithms are used.")
        return self.ask_if_correct("Does OpenVPN use strong ciphers/hashing algorithms?")
