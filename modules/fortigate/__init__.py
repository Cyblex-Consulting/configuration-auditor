from modules.fortigate.module import FortigateModule


def get_module(display, verbose=False):
    """Factory used by the module registry to instantiate this module."""
    return FortigateModule(display, verbose)
