import json
import os
import shutil

import fortios_xutils.parser

from core.module import Module
from modules.fortigate.device import FortigateDevice

# Scratch directory used by the FortiGate parser. The config is copied here
# before parsing and fortios_xutils also dumps intermediate JSON files into it.
TMP_DIR = "tmp"


class FortigateModule(Module):

    name = "fortigate"
    description = "FortiGate / FortiManager configuration"
    device_class = FortigateDevice

    def parse(self, filepath, autofix=False):
        print(f'[+] Configuration file: {filepath}')

        if not os.path.isdir(TMP_DIR):
            os.makedirs(TMP_DIR, exist_ok=True)

        reparse = True
        tmp_filepath = f'{TMP_DIR}/{os.path.basename(filepath)}'
        shutil.copyfile(filepath, tmp_filepath)

        parsed_output = None
        while reparse:
            try:
                # Check for non unicode characters; this raises so we can fix.
                with open(tmp_filepath, 'r') as file:
                    file.read()

                # Try parsing
                parsed_output = fortios_xutils.parser.parse_show_config_and_dump(
                    tmp_filepath, TMP_DIR)
                reparse = False
                os.remove(tmp_filepath)
            except TypeError as e:
                if str(e) == "dict() got multiple values for keyword argument 'config'":
                    print('[!] It seems you ran into bug '
                          'https://github.com/ssato/python-anyconfig-fortios-backend/issues/3')
                    print('    I can try to apply a dirty fix by replacing the following configuration block:')
                    print('       config loggrp-permission')
                    print('       set config read')
                    print('       end')
                    print('    by:')
                    print('       config loggrp-permission')
                    print('       set configxxx read')
                    print('       end')
                    print('    It may fail some checks that would evaluate this configuration items.')
                    if autofix:
                        print('[+] Trying to fix the issue')
                    else:
                        print('[?] Type \'yes\' to continue or Ctrl-C to quit')
                        while input() != "yes":
                            print('[?] Type \'yes\' to continue or Ctrl-C to quit')

                    # Fix the set config read issue
                    with open(tmp_filepath, 'r') as file:
                        filedata = file.read()
                    filedata = filedata.replace('set config read', 'set configxxx read')
                    with open(tmp_filepath, 'w') as file:
                        file.write(filedata)

                    reparse = True
                else:
                    raise
            except UnicodeDecodeError:
                print('[!] Parsing failed due to characters not utf-8 encoded')
                print('    I can try to remove those characters and re-parse again')
                print('    Most of the time, non utf-8 characters are in comments or non critical items, however that may fail some checks.')
                if autofix:
                    print('[+] Trying to fix the issue')
                else:
                    print('[?] Type \'yes\' to continue or Ctrl-C to quit')
                    while input() != "yes":
                        print('[?] Type \'yes\' to continue or Ctrl-C to quit')

                # Fix the encoding
                with open(tmp_filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    filedata = file.read()
                with open(tmp_filepath, 'w') as file:
                    file.write(filedata)
                reparse = True

        config = parsed_output[1]["configs"]
        print('[+] Configuration succesfully parsed')
        return self.device_class(config, self.display, self.verbose)

    def parse_json(self, filepath):
        print(f'[+] Configuration file: {filepath}')
        with open(filepath) as f:
            config = json.load(f)["configs"]
        print('[+] Configuration loaded from JSON file')
        return self.device_class(config, self.display, self.verbose)

    def load_checks(self):
        # Importing the package triggers discovery of all check subclasses.
        import modules.fortigate.checks  # noqa: F401
