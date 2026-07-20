import os
from core.checker import Checker

# Imports all python files in this folder as checks.

_PACKAGE = __name__  # e.g. "modules.fortigate.checks.cis_1_1_0"

parent_folder = os.path.dirname(__file__)
for module in os.listdir(parent_folder):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(f'{_PACKAGE}.{module[:-3]}', locals(), globals())


# Return all checker classes
def classes():
    return Checker.__subclasses__()
