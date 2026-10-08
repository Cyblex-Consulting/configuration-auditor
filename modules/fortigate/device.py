from core.device import Device
from modules.fortigate import fortiguard


class FortigateDevice(Device):

    def __init__(self, config, display, verbose=False):
        super().__init__(config, display, verbose)
        self.wan_interfaces = None
        # Fortiguard object
        self.fortiguard = fortiguard.Fortiguard()
        self.all_timezones = {
            "01":"(GMT-11:00) Midway Island, Samoa",
            "02":"(GMT-10:00) Hawaii",
            "03":"(GMT-9:00) Alaska",
            "04":"(GMT-8:00) Pacific Time (US & Canada)",
            "05":"(GMT-7:00) Arizona",
            "81":"(GMT-7:00) Baja California Sur, Chihuahua",
            "06":"(GMT-7:00) Mountain Time (US & Canada)",
            "07":"(GMT-6:00) Central America",
            "08":"(GMT-6:00) Central Time (US & Canada)",
            "09":"(GMT-6:00) Mexico City",
            "10":"(GMT-6:00) Saskatchewan",
            "11":"(GMT-5:00) Bogota, Lima,Quito",
            "12":"(GMT-5:00) Eastern Time (US & Canada)",
            "13":"(GMT-5:00) Indiana (East)",
            "74":"(GMT-4:00) Caracas",
            "14":"(GMT-4:00) Atlantic Time (Canada)",
            "77":"(GMT-4:00) Georgetown",
            "15":"(GMT-4:00) La Paz",
            "87":"(GMT-4:00) Paraguay",
            "16":"(GMT-3:00) Santiago",
            "17":"(GMT-3:30) Newfoundland",
            "18":"(GMT-3:00) Brasilia",
            "19":"(GMT-3:00) Buenos Aires",
            "20":"(GMT-3:00) Nuuk (Greenland)",
            "75":"(GMT-3:00) Uruguay",
            "21":"(GMT-2:00) Mid-Atlantic",
            "22":"(GMT-1:00) Azores",
            "23":"(GMT-1:00) Cape Verde Is.",
            "24":"(GMT) Monrovia",
            "80":"(GMT) Greenwich Mean Time",
            "79":"(GMT) Casablanca",
            "25":"(GMT) Dublin, Edinburgh, Lisbon, London, Canary Is.",
            "26":"(GMT+1:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna",
            "27":"(GMT+1:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague",
            "28":"(GMT+1:00) Brussels, Copenhagen, Madrid, Paris",
            "78":"(GMT+1:00) Namibia",
            "29":"(GMT+1:00) Sarajevo, Skopje, Warsaw, Zagreb",
            "30":"(GMT+1:00) West Central Africa",
            "31":"(GMT+2:00) Athens, Sofia, Vilnius",
            "32":"(GMT+2:00) Bucharest",
            "33":"(GMT+2:00) Cairo",
            "34":"(GMT+2:00) Harare, Pretoria",
            "35":"(GMT+2:00) Helsinki, Riga, Tallinn",
            "36":"(GMT+2:00) Jerusalem",
            "37":"(GMT+3:00) Baghdad",
            "38":"(GMT+3:00) Kuwait, Riyadh",
            "83":"(GMT+3:00) Moscow",
            "84":"(GMT+3:00) Minsk",
            "40":"(GMT+3:00) Nairobi",
            "85":"(GMT+3:00) Istanbul",
            "41":"(GMT+3:30) Tehran",
            "42":"(GMT+4:00) Abu Dhabi, Muscat",
            "43":"(GMT+4:00) Baku",
            "39":"(GMT+3:00) St. Petersburg, Volgograd",
            "44":"(GMT+4:30) Kabul",
            "46":"(GMT+5:00) Islamabad, Karachi, Tashkent",
            "47":"(GMT+5:30) Kolkata, Chennai, Mumbai, New Delhi",
            "51":"(GMT+5:30) Sri Jayawardenepara",
            "48":"(GMT+5:45) Kathmandu",
            "45":"(GMT+5:00) Ekaterinburg",
            "49":"(GMT+6:00) Almaty, Novosibirsk",
            "50":"(GMT+6:00) Astana, Dhaka",
            "52":"(GMT+6:30) Rangoon",
            "53":"(GMT+7:00) Bangkok, Hanoi, Jakarta",
            "54":"(GMT+7:00) Krasnoyarsk",
            "55":"(GMT+8:00) Beijing, ChongQing, HongKong, Urumgi, Irkutsk",
            "56":"(GMT+8:00) Ulaan Bataar",
            "57":"(GMT+8:00) Kuala Lumpur, Singapore",
            "58":"(GMT+8:00) Perth",
            "59":"(GMT+8:00) Taipei",
            "60":"(GMT+9:00) Osaka, Sapporo, Tokyo, Seoul",
            "62":"(GMT+9:30) Adelaide",
            "63":"(GMT+9:30) Darwin",
            "61":"(GMT+9:00) Yakutsk",
            "64":"(GMT+10:00) Brisbane",
            "65":"(GMT+10:00) Canberra, Melbourne, Sydney",
            "66":"(GMT+10:00) Guam, Port Moresby",
            "67":"(GMT+10:00) Hobart",
            "68":"(GMT+10:00) Vladivostok",
            "69":"(GMT+10:00) Magadan",
            "70":"(GMT+11:00) Solomon Is., New Caledonia",
            "71":"(GMT+12:00) Auckland, Wellington",
            "72":"(GMT+12:00) Fiji, Kamchatka, Marshall Is.",
            "00":"(GMT+12:00) Eniwetok, Kwajalein",
            "82":"(GMT+12:45) Chatham Islands",
            "73":"(GMT+13:00) Nuku'alofa",
            "86":"(GMT+13:00) Samoa",
            "76":"(GMT+14:00) Kiritimati"
        }
    
    # Returns the config bloc in config dict
    def get_config(self, chapter=None):
        if chapter is None:
            return self.config
        else:
            for block in self.config:
                if "config" in block.keys() and block["config"] == chapter:
                    return block
            return None
    
    # Returns all firewall interfaces
    def get_interfaces(self):
        config_system_interface = self.get_config("system interface")
        interfaces = config_system_interface["edits"]
        return interfaces
        
    # Returns all firewall zones
    def get_zones(self):
        config_system_zone = self.get_config("system zone")
        zones = config_system_zone["edits"]
        return zones

    # Prints the interfaces for the --interfaces flag
    def show_interfaces(self):
        print('[+] The following interfaces exist on the device:')
        for interface in self.get_interfaces():
            print(f'[-] {interface["edit"]}')
            if "vdom" in interface.keys():
                print(f'     | vdom {interface["vdom"]}')
            if "type" in interface.keys():
                print(f'     | type {interface["type"]}')
            if "status" in interface.keys():
                print(f'     | status {interface["status"]}')
            if "ip" in interface.keys():
                ips = ", ".join(interface["ip"])
                print(f'     | ip {ips}')

    # Prints the zones for the --zones flag
    def show_zones(self):
        print('[+] The following zones exist on the device:')
        for zone in self.get_zones():
            print(f'[-] {zone["edit"]}')
            if "interface" in zone.keys():
                if isinstance(zone["interface"], list):
                    child_interfaces = ", ".join(zone["interface"])
                else:
                    child_interfaces = zone["interface"]
                print(f'     | interfaces {child_interfaces}')

    
    # Returns WAN interfaces. If unknown, prompt the user.
    def get_wan_interfaces(self):
        if self.wan_interfaces is None:
            question_context = []
            question_context.append('All these interfaces exist on the device:')
            interfaces = self.get_interfaces()
            for interface in interfaces:
                name = interface["edit"]
                question_context.append(f'- {name}')
                
            question_context.append('All these zones exist on the device:')
            zones = self.get_zones()
            for zone in zones:
                name = zone["edit"]
                if isinstance(zone["interface"], list):
                    child_interfaces = ", ".join(zone["interface"])
                else:
                    child_interfaces = zone["interface"]
                question_context.append(f'- {name}: {child_interfaces}')
                
            answer = self.display.ask(question_context, "Enter the WAN interfaces or zones, comma separated and case sensitive (for instance: port1,port2,zone_wan)")
                        
            self.set_wan_interfaces(answer.replace(" ", "").split(","))    
        
        return self.wan_interfaces
    
    # Configures interfaces that should be considered WAN
    def set_wan_interfaces(self, interfaces_names):
        self.wan_interfaces = []
        
        for interface in self.get_interfaces():
            if interface["edit"] in interfaces_names:
                self.wan_interfaces.append(interface)
                
    # Returns firewall policies. Allows filtering
    def get_policies(self, srcintfs=None, dstintfs=None, actions=None):
        config_firewall_policy = self.get_config("firewall policy")
        if config_firewall_policy is None:
            return []
        
        policies = config_firewall_policy['edits']

        result = []        
        for policy in policies:
            if srcintfs is not None:
                if policy["srcintf"] not in [x["edit"] for x in srcintfs]:
                    continue
                
            if dstintfs is not None:
                if policy["dstintf"] not in [x["edit"] for x in dstintfs]:
                    continue
                
            if actions is not None:
                if "action" not in policy.keys():
                    continue
                
                if policy["action"] not in actions:
                    continue
            
            result.append(policy)

        return result
    
    # Returns ips sensors. Allows filtering
    def get_ips_sensors(self, names=None):
        config_ips_sensors = self.get_config("ips sensor")
        if config_ips_sensors is None:
            return []
        
        ips_sensors = config_ips_sensors['edits']
        
        result = []
        for ips_sensor in ips_sensors:
            if names is not None:
                if ips_sensor["edit"] not in names:
                    continue
            
            result.append(ips_sensor)
            
        return result
    
    # Return A/V profiles. Allows filtering
    def get_av_profiles(self, names=None):
        config_av_profiles = self.get_config("antivirus profile")
        if config_av_profiles is None:
            return []
        
        av_profiles = config_av_profiles['edits']
        
        result = []
        for av_profile in av_profiles:
            if names is not None:
                if av_profile["edit"] not in names:
                    continue
            
            result.append(av_profile)
            
        return result
    
    # Returns DNS Filter profiles. Allows filtering
    def get_dnsfilter_profiles(self, names=None):
        config_dnsfilter_profiles = self.get_config("dnsfilter profile")
        if config_dnsfilter_profiles is None:
            return []
        
        dnsfilter_profiles = config_dnsfilter_profiles['edits']
        
        result = []
        for dnsfilter_profile in dnsfilter_profiles:
            if names is not None:
                if dnsfilter_profile["edit"] not in names:
                    continue
            
            result.append(dnsfilter_profile)
            
        return result
    
    # Returns all service groups that includes a protocol (for instance "Windows AD" is returned when protocols = ["DNS"])
    def get_service_groups_containing_protocols(self, protocols=None):
        config_firewall_service_groups = self.get_config("firewall service group")
        if config_firewall_service_groups is None:
            return []
        
        service_groups = config_firewall_service_groups["edits"]
        
        result = []
        for service_group in service_groups:
            if protocols is not None:
                for protocol in protocols:
                    if protocol in service_group["member"]:
                        if not service_group["edit"] in result:
                            result.append(service_group["edit"])
            else:
                result.append(service_group)

        return result

    # Returns App Control profiles. Allows filtering
    def get_appcontrol_profiles(self, names=None):
        config_appcontrol_profiles = self.get_config("application list")
        if config_appcontrol_profiles is None:
            return []
        
        appcontrol_profiles = config_appcontrol_profiles['edits']
        
        result = []
        for appcontrol_profile in appcontrol_profiles:
            if names is not None:
                if appcontrol_profile["edit"] not in names:
                    continue
            
            result.append(appcontrol_profile)
            
        return result