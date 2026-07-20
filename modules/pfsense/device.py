from core.device import Device


class PfsenseDevice(Device):
    """pfSense device adapter (SKELETON).

    pfSense stores its configuration as a single XML document (config.xml).
    This adapter is a placeholder: the parser produces whatever structure the
    module chooses, and the accessors below need to be implemented to expose
    interfaces, rules, etc. to checks.

    TODO: implement real accessors once the pfSense parser is written.
    """

    def get_config(self, chapter=None):
        # TODO: navigate the parsed pfSense config (e.g. an ElementTree or a
        # dict produced from config.xml) and return the requested section.
        raise NotImplementedError("pfSense get_config is not implemented yet")

    def get_interfaces(self):
        # TODO: return the <interfaces> section of config.xml.
        raise NotImplementedError("pfSense get_interfaces is not implemented yet")

    def get_wan_interfaces(self):
        # TODO: return the WAN interfaces (pfSense marks one as "wan").
        raise NotImplementedError("pfSense get_wan_interfaces is not implemented yet")

    def set_wan_interfaces(self, interfaces_names):
        # TODO: implement WAN interface selection.
        raise NotImplementedError("pfSense set_wan_interfaces is not implemented yet")
