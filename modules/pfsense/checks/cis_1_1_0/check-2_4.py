from core.checker import Checker

# Commonly-shipped default account names (per the benchmark's Additional Info).
KNOWN_DEFAULT_ACCOUNTS = [
    "admin", "guest", "user", "root", "administrator",
    "operator", "supervisor", "demo",
]


class Check_Pfsense_2_4(Checker):
    """2.4 Ensure all default accounts are either disabled or utilize strong passwords.

    Password strength cannot be assessed from config.xml, so this is a manual
    check. We list any known default account names found to assist the operator.
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "2.4"
        self.title = "Ensure all default accounts are either disabled or utilize strong passwords"
        self.levels = [1, 2]
        self.auto = False
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def do_check(self):
        users = self.device.get_users()
        found = []
        for user in users:
            if not isinstance(user, dict):
                continue
            name = user.get("name", "")
            if name in KNOWN_DEFAULT_ACCOUNTS:
                disabled = "disabled" if "disabled" in user else "ENABLED"
                found.append(f'{name} ({disabled})')

        if found:
            self.add_question_context("Known default accounts present:")
            for f in found:
                self.add_question_context(f'- {f}')
        else:
            self.add_question_context("No known default account names found in config.")
        self.add_question_context("Confirm all default accounts are disabled or use strong passwords.")
        return self.ask_if_correct("Are default accounts disabled or using strong passwords?")
