class Device:
    """Vendor-agnostic base class for a parsed device configuration.

    A Device wraps the parsed configuration (whatever shape the vendor parser
    produces) and exposes accessors used by checks. The only method the generic
    core relies on is `get_config`. Vendor subclasses add their own typed
    helpers (interfaces, zones, policies, ...) on top of it.
    """

    def __init__(self, config, display, verbose=False):
        self.config = config
        self.display = display
        self.verbose = verbose

    def get_config(self, chapter=None):
        """Return a configuration block for the given chapter.

        Vendor subclasses must implement the chapter lookup that matches their
        parsed configuration structure.
        """
        raise NotImplementedError

    def get_interfaces(self):
        """Return the list of interfaces (vendor specific)."""
        raise NotImplementedError

    def get_wan_interfaces(self):
        """Return the list of WAN interfaces (vendor specific)."""
        raise NotImplementedError

    def set_wan_interfaces(self, interfaces_names):
        """Configure which interfaces are considered WAN (vendor specific)."""
        raise NotImplementedError

    # -- CLI helpers (--interfaces / --zones) ------------------------------
    #
    # These render the vendor's interfaces/zones for the entrypoint's
    # `--interfaces` and `--zones` flags. The parsed config shape is vendor
    # specific, so each Device subclass formats its own output. The defaults
    # below report that the feature is unsupported for this vendor.

    def show_interfaces(self):
        """Print the device interfaces. Override per vendor."""
        print(f'[!] The "--interfaces" option is not supported by this module')

    def show_zones(self):
        """Print the device zones. Override per vendor."""
        print(f'[!] The "--zones" option is not supported by this module')
