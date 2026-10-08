import bcrypt

from core.checker import Checker


class Check_Pfsense_3_4(Checker):
    """3.4 Ensure default password of admin is changed.

    Password hashes are not exposed for comparison here, so this is validated
    manually (try logging in with admin/pfsense).
    """

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "3.4"
        self.title = "Ensure default password of admin is changed"
        self.levels = [1, 2]
        self.auto = True
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "CIS"

    def _verify_password(self, candidate, bcrypt_hash):
        # Some bcrypt implementations expect 2a/2b instead of 2y
        if bcrypt_hash.startswith("$2y$"):
            bcrypt_hash = "$2b$" + bcrypt_hash[4:]

        return bcrypt.checkpw(
            candidate.encode(),
            bcrypt_hash.encode()
        )

    def _get_admin_password_hash(self):
        users = self.device.get_users()
        for user in users:
            if not isinstance(user, dict):
                continue
            name = user.get("name", "")
            if name == "admin":
                return user.get("bcrypt-hash", "")
        return None

    def do_check(self):

        password_hash = self._get_admin_password_hash()
        if not password_hash:
            self.set_message("Could not retrieve admin password hash")
            return False

        # Default password is "pfsense", we try that as well as trivial ones
        candidates = ["pfsense", "admin", "password", "123456"]
        for candidate in candidates:
            if self._verify_password(candidate, password_hash):
                self.set_message("Default password is still in use")
                return False

        self.set_message(f"Password for admin has been changed and is not one of : {', '.join(candidates)}")
        return True

