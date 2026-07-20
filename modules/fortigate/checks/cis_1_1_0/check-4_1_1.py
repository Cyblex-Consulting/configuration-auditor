from core.checker import Checker

class Check_CIS_4_1_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.1.1"
        self.title = "Detect Botnet Connections"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        wan_interfaces = self.firewall.get_wan_interfaces()
        wan_policies = self.firewall.get_policies(dstintfs=wan_interfaces, actions=["accept"])
        
        fail = False
        for policy in wan_policies:
            if "ips-sensor" not in policy.keys():
                if "name" in policy.keys():
                    self.add_message(f'WAN Policy {policy["name"]} has no IPS profile')
                else:
                    self.add_message(f'WAN Policy {policy["uuid"]} has no IPS profile')
                fail = True
            else:
                ips_sensors = self.firewall.get_ips_sensors(names=[policy["ips-sensor"]])
                print(ips_sensors)
                ips_sensor_block_botnet = False
                for ips_sensor in ips_sensors:
                    if "scan-botnet-connections" in ips_sensor.keys() and ips_sensor["scan-botnet-connections"] == "block":
                        ips_sensor_block_botnet = True
                        break
                if not ips_sensor_block_botnet:
                    if "name" in policy.keys():
                        self.add_message(f'WAN Policy {policy["name"]} has IPS profile "{policy["ips-sensor"]}" which is not blocking botnets')
                    else:
                        self.add_message(f'WAN Policy {policy["uuid"]} has IPS profile "{policy["ips-sensor"]}" which is not blocking botnets')
                    fail = True
        return not fail