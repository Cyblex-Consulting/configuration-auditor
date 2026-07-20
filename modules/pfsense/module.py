from core.module import Module
from modules.pfsense.device import PfsenseDevice


class PfsenseModule(Module):
    """pfSense module (SKELETON).

    This is a minimal placeholder demonstrating how a second vendor plugs into
    Configuration Auditor. Parsing and checks are not implemented yet.

    pfSense configuration is a single XML file (config.xml). A real
    implementation would parse it (e.g. with xml.etree.ElementTree) into a
    structure consumed by PfsenseDevice, then add checks under
    modules/pfsense/checks/.
    """

    name = "pfsense"
    description = "pfSense configuration (skeleton, not yet implemented)"
    device_class = PfsenseDevice

    def parse(self, filepath, autofix=False):
        # TODO: parse the pfSense config.xml file into a structure that
        # PfsenseDevice can navigate, then:
        #   return self.device_class(parsed_config, self.display, self.verbose)
        raise NotImplementedError(
            "The pfSense module is a skeleton: configuration parsing is not "
            "implemented yet.")

    def load_checks(self):
        # Importing the package triggers discovery of any check subclasses.
        import modules.pfsense.checks  # noqa: F401
