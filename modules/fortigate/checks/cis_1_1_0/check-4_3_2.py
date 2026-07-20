from core.checker import Checker

class Check_CIS_4_3_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.3.2"
        self.title = "Ensure DNS Filter logs all DNS queries and responses"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        dnsfilter_profiles = self.firewall.get_dnsfilter_profiles()
        
        fail = False

        if len(dnsfilter_profiles) == 0:
            self.add_message('No DNS filter profile')
            return False
        
        for dnsfilter_profile in dnsfilter_profiles:
            if "log-all-domain" not in dnsfilter_profile.keys():
                self.add_message(f'"log-all-domain" not configured in DNS filter policy "{dnsfilter_profile["edit"]}"')
                fail = True
            elif dnsfilter_profile["log-all-domain"] != "enable":
                self.add_message(f'"log-all-domain" not enabled in DNS filter policy "{dnsfilter_profile["edit"]}"')
                fail = True
        
        if not fail:
            self.add_message('All policies allowing DNS have a filter policy with "log-all-domain enable"')
            
                           
        return not fail