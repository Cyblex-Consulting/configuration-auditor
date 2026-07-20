from core.checker import Checker

class Check_CIS_3_5(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "3.5"
        self.title = "Ensure firewall policy denying all traffic to/from Tor or malicious server IP addresses using ISDB"
        self.levels = [1]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_firewall_policy = self.get_config("firewall policy")

        if config_firewall_policy is None:
            self.set_message(f'No \"config firewall policy\" block defined')
            return False

        fail = False
        
        if len(config_firewall_policy['edits']) > 0:
            found_tor_inbound_block = False
            found_tor_outbound_block = False
            for edit in config_firewall_policy['edits']:
                if 'internet-service-src-name' in edit.keys():
                    if "Tor-Exit.Node" in edit['internet-service-src-name'] or "Tor-Relay.Node" in edit['internet-service-src-name']:
                        found_tor_inbound_block = True
                        if 'name' in edit.keys():
                            self.add_message(f'Inbound Tor traffic blocked in rule \"{edit["name"]}\"')
                        else:
                            self.add_message(f'Inbound Tor traffic blocked in rule {edit["uuid"]}')
                elif 'internet-service-dst-name' in edit.keys():
                    if "Tor-Exit.Node" in edit['internet-service-dst-name'] or "Tor-Relay.Node" in edit['internet-service-dst-name']:
                        found_tor_outbound_block = True
                        if 'name' in edit.keys():
                            self.add_message(f'Outbound Tor traffic blocked in rule \"{edit["name"]}\"')
                        else:
                            self.add_message(f'Outbound Tor traffic blocked in rule {edit["uuid"]}')
        else:
            self.add_message('There is no policy defined')

        if not found_tor_inbound_block:
            self.add_message('No rule to block inbound Tor traffic')

        if not found_tor_outbound_block:
            self.add_message('No rule to block outbound Tor traffic')

        return found_tor_inbound_block and found_tor_outbound_block
