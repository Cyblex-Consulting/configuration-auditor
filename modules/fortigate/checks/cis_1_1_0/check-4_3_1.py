from core.checker import Checker

class Check_CIS_4_3_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.3.1"
        self.title = "Enable Botnet C&C Domain Blocking DNS Filter"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        policies = self.firewall.get_policies(actions=["accept"])

        fail = False

        # Check that all policies allowing DNS traffic have a DNS filter
        dns_services = ["DNS", "TCP-53", "UDP-53", "ALL"]
        dns_services.extend(x for x in self.firewall.get_service_groups_containing_protocols(dns_services))

        dns_services_string = ", ".join(dns_services)
        self.add_message(f'The following services are including DNS : {dns_services_string}')
        
        used_dnsfilter_profiles = []
        for policy in policies:
            if "service" in policy.keys():
                services = policy["service"]
                for service in services:
                    if service in dns_services:
                        if "dnsfilter-profile" not in policy.keys():
                            if "name" in policy.keys():
                                self.add_message(f'No DNS Filter for policy "{policy["name"]}" which uses service {service}')
                            else:
                                self.add_message(f'No DNS Filter for policy "{policy["uuid"]}" which uses service {service}')
                            fail = True
                        else:
                            used_dnsfilter_profiles.append(policy["dnsfilter-profile"])


        # Check that all used DNS profile are configured to block botnets
        used_dnsfilter_profiles=["default"]
        dnsfilter_profiles = self.firewall.get_dnsfilter_profiles(names=used_dnsfilter_profiles)
        if len(dnsfilter_profiles) == 0:
            self.add_message('No DNS filter profile')
            return False
        
        for dnsfilter_profile in dnsfilter_profiles:
            if "block-botnet" not in dnsfilter_profile.keys():
                self.add_message(f'"block-botnet" not configured in DNS filter policy "{dnsfilter_profile["edit"]}"')
                fail = True
            elif dnsfilter_profile["block-botnet"] != "enable":
                self.add_message(f'"block-botnet" not enabled in DNS filter policy "{dnsfilter_profile["edit"]}"')
                fail = True
        
        if not fail:
            self.add_message('All policies allowing DNS have a filter policy with "block-botnet enable"')
            
                           
        return not fail