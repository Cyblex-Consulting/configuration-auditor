from core.checker import Checker

class Check_CIS_6_1_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "6.1.1"
        self.title = "Apply a Trusted Signed Certificate for VPN Portal"
        self.levels = [2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_vpnssl_settings= self.get_config("vpn ssl settings")
        
        if config_vpnssl_settings is None:
            self.add_message("No SSL VPN configured for this host")
            return True
        
        server_cert_name = config_vpnssl_settings["servercert"]
        
        # Certificate content cannot be retrieved and displayed due to bug https://github.com/ssato/python-anyconfig-fortios-backend/issues/4
        
        self.add_question_context(f'Certificate name for the SSL VPN is : {server_cert_name}')

        return self.ask_if_correct('Is it a trusted certificate?')
