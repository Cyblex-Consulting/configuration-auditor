import xml.etree.ElementTree as ET

from core.module import Module
from modules.pfsense.device import PfsenseDevice


class PfsenseModule(Module):
    """pfSense module.

    pfSense configuration is a single XML file (config.xml) rooted at
    <pfsense>. This module parses it with the standard library into nested
    dicts/lists that PfsenseDevice navigates, then runs the CIS pfSense
    Firewall Benchmark checks.
    """

    name = "pfsense"
    description = "pfSense configuration"
    device_class = PfsenseDevice

    def parse(self, filepath, autofix=False):
        print(f'[+] Configuration file: {filepath}')
        try:
            tree = ET.parse(filepath)
        except ET.ParseError as e:
            raise ValueError(f'Failed to parse pfSense config.xml: {e}')

        root = tree.getroot()
        if root.tag != "pfsense":
            print(f'[!] Warning: root element is <{root.tag}>, expected <pfsense>')

        config = self._element_to_dict(root)
        print('[+] Configuration succesfully parsed')
        return self.device_class(config, self.display, self.verbose)

    def load_checks(self):
        # Importing the package triggers discovery of all check subclasses.
        import modules.pfsense.checks  # noqa: F401

    # -- XML -> dict/list conversion --------------------------------------

    @staticmethod
    def _element_to_dict(element):
        """Recursively convert an ElementTree element into dicts/lists.

        Rules:
          - An element with no children maps to its stripped text, or "" for an
            empty element (pfSense boolean flags like <enable/>).
          - An element with children maps to a dict of {child_tag: value}.
          - Repeated child tags collapse into a list preserving order.
        """
        children = list(element)
        if not children:
            return (element.text or "").strip()

        result = {}
        for child in children:
            value = PfsenseModule._element_to_dict(child)
            tag = child.tag
            if tag in result:
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(value)
            else:
                result[tag] = value
        return result
