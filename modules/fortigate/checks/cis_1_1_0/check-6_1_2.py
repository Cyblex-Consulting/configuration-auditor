from core.checker import Checker

class Check_CIS_6_1_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "6.1.2"
        self.title = "Enable Limited TLS Versions for SSL VPN"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config_vpnssl_settings= self.get_config("vpn ssl settings")
        
        if config_vpnssl_settings is None:
            self.add_message("No SSL VPN configured for this host")
            return True
        
        fail = False
        
        if "ssl-max-proto-ver" not in config_vpnssl_settings.keys():
            self.add_message("ssl-max-proto-ver not defined")
            fail = True
        else:
            ssl_max = config_vpnssl_settings["ssl-max-proto-ver"]
            if ssl_max != "tls1-3":
                self.add_message(f'Configured TLS max version is {ssl_max} and not tls1-3')
                fail = True
                
        if "ssl-min-proto-ver" not in config_vpnssl_settings.keys():
            self.add_message("ssl-min-proto-ver not defined")
            fail = True
        else:
            ssl_min = config_vpnssl_settings["ssl-min-proto-ver"]
            if ssl_min != "tls1-2":
                self.add_message(f'Configured TLS min version is {ssl_min} and not tls1-2')
                fail = True        
                
        if "banned-cipher" not in config_vpnssl_settings.keys():
            self.add_message("banned-cipher not defined")
            fail = True
        else:
            banned_ciphers = ", ".join(config_vpnssl_settings["banned-cipher"])
            self.add_message(f'Configured banned cyphers: {banned_ciphers}')
        
        if "algorithm" not in config_vpnssl_settings.keys():
            self.add_message("algorithm not defined")
            fail = True
        else:
            if config_vpnssl_settings["algorithm"] != "high":
                self.add_message(f'Strong algorithms not enforced')
                fail = True 
                
        return not fail