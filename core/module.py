from core.checker import Checker


class Module:
    """Base class for a vendor module (FortiGate, pfSense, ...).

    A module is the single integration point the generic entrypoint talks to.
    It knows how to:
      - parse a vendor configuration file into a Device
      - build a Device from an already-parsed JSON file
      - expose the checks that apply to this vendor

    Subclasses must set `name` and implement `parse`. Everything else has a
    sensible default that can be overridden.
    """

    # Short identifier used on the command line (e.g. "fortigate").
    name = None
    # Human readable description shown in help/output.
    description = ""
    # Device subclass used by this module.
    device_class = None

    def __init__(self, display, verbose=False):
        self.display = display
        self.verbose = verbose

    # -- Parsing -----------------------------------------------------------

    def parse(self, filepath, autofix=False):
        """Parse a raw vendor configuration file and return a Device."""
        raise NotImplementedError

    def parse_json(self, filepath):
        """Build a Device from an already-parsed JSON file.

        Default implementation is not provided because the JSON schema is
        vendor specific. Modules that support the `--json` flag must override.
        """
        raise NotImplementedError(
            f'Module "{self.name}" does not support pre-parsed JSON input')

    # -- Check discovery ---------------------------------------------------

    def load_checks(self):
        """Import this module's check packages.

        Checks are discovered through Checker.__subclasses__(), so a check only
        registers itself once its module is imported. Subclasses override this
        to import their `checks` package.
        """
        raise NotImplementedError

    def check_classes(self):
        """Return all discovered Checker subclasses.

        Call `load_checks()` first (the entrypoint does this).
        """
        return Checker.__subclasses__()
