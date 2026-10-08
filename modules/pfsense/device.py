from core.device import Device


class PfsenseDevice(Device):
    """pfSense device adapter.

    pfSense stores its configuration as a single XML document (config.xml)
    rooted at <pfsense>. The module parses it into nested Python dicts/lists
    (see PfsenseModule._element_to_dict): repeated tags become lists, leaf text
    becomes a string, and empty self-closing tags (pfSense "boolean" flags such
    as <enable/>) become an empty string "" (their mere presence means "on").

    Config access is done with slash-separated paths relative to the <pfsense>
    root, e.g. get_config("system/hostname") or get_config("system/webgui").
    """

    def __init__(self, config, display, verbose=False):
        super().__init__(config, display, verbose)
        self.wan_interfaces = None

    # -- Core access -------------------------------------------------------

    def get_config(self, chapter=None):
        """Return a section of the parsed config by slash-separated path.

        `chapter=None` returns the whole config dict. A path like
        "system/webgui" walks the nested dicts. Returns None if any path
        component is missing. When an intermediate component is a list (a
        repeated tag), the first element is used.
        """
        if chapter is None:
            return self.config

        node = self.config
        for part in chapter.split("/"):
            if isinstance(node, list):
                node = node[0] if node else None
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node

    def get_list(self, chapter):
        """Like get_config but always returns a list.

        pfSense repeated elements become a list, but a single occurrence is a
        dict. This normalizes both (and a missing key) to a list.
        """
        node = self.get_config(chapter)
        if node is None:
            return []
        if isinstance(node, list):
            return node
        return [node]

    def has_flag(self, chapter):
        """Return True if a pfSense boolean flag element is present.

        pfSense represents many on/off options as the presence/absence of an
        empty element (e.g. <enablesshd></enablesshd>). Presence -> parsed as
        "" (or some truthy text). This returns True when the key exists at all.
        """
        node = self.get_config(chapter)
        return node is not None

    # -- Typed helpers -----------------------------------------------------

    def get_interfaces(self):
        """Return the interfaces as a dict keyed by interface name (wan, lan...)."""
        interfaces = self.get_config("interfaces")
        return interfaces if isinstance(interfaces, dict) else {}

    def get_wan_interfaces(self):
        return self.wan_interfaces

    def set_wan_interfaces(self, interfaces_names):
        self.wan_interfaces = list(interfaces_names)

    # Prints the interfaces for the --interfaces flag.
    # pfSense interfaces are a dict keyed by logical name (wan, lan, opt1...).
    def show_interfaces(self):
        interfaces = self.get_interfaces()
        if not interfaces:
            print('[!] No interfaces found in the configuration')
            return
        print('[+] The following interfaces exist on the device:')
        for name, iface in interfaces.items():
            if not isinstance(iface, dict):
                print(f'[-] {name}')
                continue
            print(f'[-] {name}')
            if iface.get("descr"):
                print(f'     | descr {iface["descr"]}')
            if iface.get("if"):
                print(f'     | device {iface["if"]}')
            status = "enabled" if "enable" in iface else "disabled"
            print(f'     | status {status}')
            if iface.get("ipaddr"):
                ip = iface["ipaddr"]
                if iface.get("subnet"):
                    ip = f'{ip}/{iface["subnet"]}'
                print(f'     | ipv4 {ip}')
            if iface.get("ipaddrv6"):
                ip6 = iface["ipaddrv6"]
                if iface.get("subnetv6"):
                    ip6 = f'{ip6}/{iface["subnetv6"]}'
                print(f'     | ipv6 {ip6}')

    # pfSense has no concept of zones, so show_zones uses the base-class default
    # ("not supported by this module").

    def get_users(self):
        """Return the list of local user accounts (system/user)."""
        return self.get_list("system/user")

    def get_filter_rules(self):
        """Return the list of firewall filter rules (filter/rule)."""
        return self.get_list("filter/rule")

    def get_aliases(self):
        """Return the list of aliases (aliases/alias)."""
        return self.get_list("aliases/alias")
