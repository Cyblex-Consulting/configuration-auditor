import os
from core.checker import Checker

# Imports all benchmark sub-packages so their checks register themselves as
# Checker subclasses. Discovery is by Checker.__subclasses__(), NOT by file
# scanning: a check only runs if its module has been imported here.

_PACKAGE = __name__  # e.g. "modules.fortigate.checks"

parent_folder = os.path.dirname(__file__)
for folder_name in os.listdir(parent_folder):
    item = f'{parent_folder}/{folder_name}'
    if os.path.isdir(item) and folder_name[:2] != '__':
        __import__(f'{_PACKAGE}.{folder_name}', locals(), globals())


# Return all checker classes
def classes():
    return Checker.__subclasses__()
