from core.checker import Checker

class Check_CIS_2_1_6(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "2.1.6"
        self.title = "Ensure the latest firmware is installed"
        self.levels = [2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        config = self.get_config()

        for block in config:
            if "config-version" in block.keys():
                config_system_status = block
                break

        self.add_question_context(f'Reported firmware is {config_system_status["config-version"]}.')
        
        if "platform" in config_system_status.keys():
            # In fortimanager export, this is present but not in direct export
            self.add_question_context(f'Reported model is {config_system_status["platform"]}.')
            
        self.add_question_context(f'Go to https://docs.fortinet.com/upgrade-tool and check that if is the latest version.')
        
        return self.ask_if_correct("Is it the latest version and is it still supported?")