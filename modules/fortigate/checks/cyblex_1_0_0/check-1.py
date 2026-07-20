from core.checker import Checker
import re

class Check_Cyblex_1(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "1"
        self.title = "Check firewall policies that looks temporary or debug"
        self.levels = [1]
        self.auto = False
        self.benchmark_version = "1.0.0"
        self.benchmark_author = "Cyblex"

    def do_check(self):
        config_firewall_policy = self.get_config("firewall policy")

        if config_firewall_policy is None:
            self.set_message(f'No \"config policy\" block defined')
            return True
        
        REGEX = re.compile('TEMP|tmp|test|DBG|Debug|Open BAR', re.IGNORECASE)

        suspicious_rules = []
        if len(config_firewall_policy['edits']) > 0:
            
            for edit in config_firewall_policy['edits']:
                suspicious = False

                if "name" in edit.keys():
                    name = edit["name"]
                    if REGEX.search(name):
                        suspicious = True
                else:
                    name = "<no name>"
                
                if "comments" in edit.keys():
                    comments = edit['comments']

                    if len(comments) > 0:
                        # Dirty semi workaround for https://github.com/ssato/python-anyconfig-fortios-backend/issues/4
                        if isinstance(comments, list):
                            comments = " ".join(comments)

                        if REGEX.search(comments):
                            suspicious = True
                else:
                    comments = "<no comment>"

                if suspicious:
                    suspicious_rules.append({"uuid": edit["uuid"], "name": name, "comments": comments})
                        
            if len(suspicious_rules) > 0:
                self.add_question_context("The following policies have suspicious name or suspicious comment:")
                for rule in suspicious_rules:
                    self.add_question_context(f"{rule['uuid']}: {rule['name']}")
                    self.add_question_context(f"{rule['comments']}")
                return self.ask_if_correct()

            else:
                self.set_message("No policy with suspicious name found")
                return True
        else:
            self.add_message('There is no policy defined')
            return True

        return None
