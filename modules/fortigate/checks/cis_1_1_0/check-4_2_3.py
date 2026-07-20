from core.checker import Checker

class Check_CIS_4_2_3(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)
        
        self.id = "4.2.3"
        self.title = "Enable Outbreak Prevention Database"
        self.levels = [2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        interfaces = self.firewall.get_interfaces()
        av_profiles = self.firewall.get_av_profiles()
        
        nb_fail = 0
        for av_profile in av_profiles:
            for config in av_profile["configs"]:
                if "outbreak-prevention" not in config.keys():
                    self.add_message(f'outbreak-prevention not defined in A/V policy "{av_profile["edit"]}" for {config["config"]}')
                    nb_fail += 1
                elif config["outbreak-prevention"] != "block":
                    self.add_message(f'outbreak-prevention not blocking in A/V policy "{av_profile["edit"]}" for {config["config"]}')
                    nb_fail += 1
        
        # Display results
        self.add_message(f'{nb_fail} policies have no A/V outbreak protection')
            
        return nb_fail == 0