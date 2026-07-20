from core.checker import Checker

class Check_CIS_2_1_4(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.1.4"
        self.title = "Ensure correct system time is configured through NTP"
        self.levels = [1]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):

        config_system_ntp = self.get_config("system ntp")

        if config_system_ntp is None:
            self.set_message(f'No "config system ntp" bloc in configuration file')
            return False
        
        if "type" not in config_system_ntp.keys():
            self.set_message(f'typesync key is not defined')
            return False

        if not config_system_ntp["type"] == "custom":
            self.set_message(f'type is set to \"{config_system_ntp["type"]}\" and not \"custom\"')
            return False

        if len(config_system_ntp["configs"]) < 1:
            self.set_message('No sub config for \"config system ntp\"')
            return False     

        found_config = False
        for config in config_system_ntp["configs"]:
            if config['config'] == 'ntpserver':
                found_config = True
                if len(config['edits']) < 1:
                    self.set_message('No NTP server defined')
                    return False 
                for edit in config['edits']:
                    ntp_server = edit['server']
                    if not self.is_ip(ntp_server) and not self.is_fqdn(ntp_server):
                        self.set_message(f'{ntp_server} is neither an IP nor a valid hostname')
                        return False
                    self.add_message(ntp_server)
            else:
                pass
        if not found_config:
            self.set_message('No \"config ntpserver\" block defined')
            return False              
                
        return True