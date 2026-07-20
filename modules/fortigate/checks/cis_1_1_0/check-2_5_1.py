from core.checker import Checker

class Check_CIS_2_5_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.5.1"
        self.title = "Ensure High Availability Configuration"
        self.levels = [2]
        self.auto = True
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_ha = self.get_config("system ha")

        if config_system_ha is None:
            self.set_message(f'No \"config system ha\" block defined')
            return False

        if "mode" not in config_system_ha.keys():
            self.set_message(f'No HA mode configured')
            return False

        if not config_system_ha["mode"] == "a-p":
            self.set_message(f'HA Mode is {config_system_ha["mode"]} and not \"a-p\"')
            return False

        if "group-name" not in config_system_ha.keys():
            self.set_message(f'No HA group name configured')
            return False
        else:
            self.add_message(f'HA Group is {config_system_ha["group-name"]}')

        if "password" not in config_system_ha.keys():
            self.set_message(f'No HA password configured')
            return False

        if "hbdev" not in config_system_ha.keys():
            self.set_message(f'No HA Heartbeat configured')
            return False
        else:
            self.add_message(f'HA hearbeat configuration : {config_system_ha["hbdev"]}')

        return True
