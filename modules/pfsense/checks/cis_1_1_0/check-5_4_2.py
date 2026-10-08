from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64

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
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def _show_cert_details(self, crt):

        pem = base64.b64decode(crt).decode()

        if not pem:
            print("Empty certificate")
            return

        # Load certificate
        cert = x509.load_pem_x509_certificate(pem.encode())

        # Common Name
        try:
            cn = cert.subject.get_attributes_for_oid(
                x509.NameOID.COMMON_NAME
            )[0].value
        except IndexError:
            pass

        return cert

    def _get_ca(self, caref):
        ca_list = self.device.get_list("ca")
        for ca in ca_list:
            if ca["refid"] == caref:
                return ca
        return None

    def do_check(self):
        openvpnservers = self.device.get_list("openvpn/openvpn-server")
        if not openvpnservers:
            self.set_message("No OpenVPN server configured under openvpn/openvpn-server")
            return True
    
        for server in openvpnservers:
            caref = server["caref"]
            ca = self._get_ca(caref)
            if not ca:
                self.add_question_context(f"OpenVPN server '{server['vpnid']}' uses CA refid: {caref} which is not found in config.xml")
                result = False
            else:
                cert = self._show_cert_details(ca["crt"])
                if not cert:
                    print("Error: certificate is empty")
                    return False
                self.add_question_context((f'OpenVPN server {server["vpnid"]} uses CA refid: {ca["refid"]} ({ca["descr"]})'))
                self.add_question_context(f"    Subject: {cert.subject.rfc4514_string()}")
                self.add_question_context(f"    Issuer : {cert.issuer.rfc4514_string()}")
                self.add_question_context(f"    Valid from: {cert.not_valid_before_utc}")
                self.add_question_context(f"    Valid until: {cert.not_valid_after_utc}")
                self.add_question_context(f"    SHA256: {cert.fingerprint(hashes.SHA256()).hex()}")

                return self.ask_if_correct("Is the VPN portal certificate signed by a trusted CA?")
