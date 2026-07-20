from modules.pfsense.module import PfsenseModule


def get_module(display, verbose=False):
    """Factory used by the module registry to instantiate this module."""
    return PfsenseModule(display, verbose)
