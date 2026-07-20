from core.checker import Checker

class Check_Example_Manual(Checker):

    def __init__(self, firewall, display, verbose=False):
        
        super().__init__(firewall, display, verbose)

        self.id = "1.1.1"
        self.title = "Example Manual Check"
        self.levels = [1, 2]
        self.auto = False
        self.enabled = False # Remove this line to enable
        self.benchmark_author = "Example Org."

    def do_check(self):
        config = self.get_config("system auto-install")

        self.add_question_context("Test Step")

        return self.ask_if_correct()
