from core.checker import Checker

class Check_CIS_2_5_2(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.5.2"
        self.title = "Ensure \"Monitor Interfaces\" for High Availability Devices is Enabled"
        self.levels = [1]
        self.auto = False
        self.enabled = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"


    def do_check(self):
        config_system_ha = self.get_config("system ha")

        if config_system_ha is None:
            self.set_message(f'No \"config system ha\" block defined')
            return False

        if "monitor" not in config_system_ha.keys():
            self.set_message(f'No HA monitor interfaces configured')
            return False

        monitored_interfaces = config_system_ha["monitor"]

        self.add_question_context('The following physical interfaces are not monitored for HA:')
        for interface in self.firewall.get_interfaces():
            if "type" in interface.keys() and interface["type"] == "physical":
                if interface["edit"] not in monitored_interfaces:
                    self.add_question_context(f'{interface["edit"]}')
                    
        return self.ask_if_correct()
