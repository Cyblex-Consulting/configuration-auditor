import importlib
import os

MODULES_PACKAGE = "modules"


def available_modules():
    """Return the list of available module names.

    A module is any sub-package of `modules/` that exposes a `get_module()`
    factory in its __init__.py.
    """
    modules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), MODULES_PACKAGE)
    names = []
    for entry in sorted(os.listdir(modules_dir)):
        path = os.path.join(modules_dir, entry)
        if os.path.isdir(path) and not entry.startswith('__'):
            names.append(entry)
    return names


def load_module(name, display, verbose=False):
    """Load and instantiate a vendor module by name.

    Raises ValueError if the module does not exist or is malformed.
    """
    if name not in available_modules():
        raise ValueError(
            f'Unknown module "{name}". Available modules: '
            f'{", ".join(available_modules())}')

    try:
        pkg = importlib.import_module(f'{MODULES_PACKAGE}.{name}')
    except ImportError as e:
        raise ValueError(f'Failed to import module "{name}": {e}')

    if not hasattr(pkg, 'get_module'):
        raise ValueError(
            f'Module "{name}" does not expose a get_module() factory')

    return pkg.get_module(display, verbose)
