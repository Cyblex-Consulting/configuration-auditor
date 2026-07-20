#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

from core.display import Display
from core.registry import available_modules, load_module

modules_list = available_modules()

parser = argparse.ArgumentParser(
    description='Configuration Auditor - apply a security benchmark to a device '
                'configuration file. '
                'Example: configuration-auditor.py -m fortigate -q -o results.csv '
                '-l 1 2 -w WAN1 WAN2 --autofix firewall.conf')
parser.add_argument('-m', '--module', required=True, choices=modules_list,
                    help='Configuration module to use (required). '
                         f'Available: {", ".join(modules_list)}')
parser.add_argument('-q', '--quiet', help='Not interactive: ignore manual steps', action='store_true')
parser.add_argument('-v', '--verbose', help='Increase verbosity', action='store_true')
parser.add_argument('-j', '--json', help='Input file is json already parsed by the module', action='store_true')
parser.add_argument('-o', '--output', help='Output CSV File')
parser.add_argument('-l', '--levels', help='Levels to check. (default: 1)', nargs='+', default="1")
parser.add_argument('-i', '--ids', help='Checks id to perform. (default: all if applicable)', nargs='+', default=None)
parser.add_argument('-c', '--resume', help='Resume an audit that was already started. Automatic items are re-checked but manually set values are retrieved from cache.', action='store_true')
parser.add_argument('-w', '--wan', help='List of wan interfaces separated by spaces (example: --wan port1 port2)', nargs='+', default=None)
parser.add_argument('--interfaces', help='Show list of interfaces and exit', action='store_true')
parser.add_argument('--zones', help='Show list of zones and exit', action='store_true')
parser.add_argument('--autofix', help='Automatically try to fix errors in input file', action='store_true')
parser.add_argument('config', help='Configuration file exported from the device', nargs=1)
args = parser.parse_args()

filepath = args.config[0]
verbose = args.verbose
quiet = args.quiet
outputfile = args.output

# Display object
display = Display()

# Load the requested vendor module
try:
    module = load_module(args.module, display, verbose)
except ValueError as e:
    print(f'[!] {e}')
    exit(-1)

print(f'[+] Using module: {module.name} ({module.description})')

# Cache file is scoped per module so different vendors don't collide.
cache_file_path = str(Path.home()) + f'/.cache/configuration-auditor-{module.name}.json'

# Create/Open cache file
if not os.path.exists(cache_file_path):
    if args.resume:
        print('[!] Cannot resume this benchmark because there is no cache file')
        exit(-1)
    else:
        print(f'[!] Creating local cache file in {cache_file_path}')
        cache_file = open(cache_file_path, mode='a')
        cache_file.write("{}")
        cache_file.close()
cache_file = open(cache_file_path, "r+")
cache = json.load(cache_file)
cache_file.close()

if filepath not in cache.keys():
    # There is no cache for this configuration file
    if args.resume:
        print(f'[!] Cannot resume this benchmark because there is no cache results for config {filepath}')
        exit(-1)
    cached_results = {}
else:
    cached_results = cache[filepath]

# Parse the configuration file into a Device via the selected module
try:
    if args.json:
        device = module.parse_json(filepath)
    else:
        device = module.parse(filepath, autofix=args.autofix)
except NotImplementedError as e:
    print(f'[!] {e}')
    exit(-1)

if args.wan is not None:
    print(f'[+] Configuring WAN interfaces: {", ".join(args.wan)}')
    device.set_wan_interfaces(args.wan)

# Display interfaces
if args.interfaces:
    print('[+] The following interfaces exist on the device:')
    for interface in device.get_interfaces():
        print(f'[-] {interface["edit"]}')
        if "vdom" in interface.keys():
            print(f'     | vdom {interface["vdom"]}')
        if "type" in interface.keys():
            print(f'     | type {interface["type"]}')
        if "status" in interface.keys():
            print(f'     | status {interface["status"]}')
        if "ip" in interface.keys():
            ips = ", ".join(interface["ip"])
            print(f'     | ip {ips}')
    exit(0)

# Display zones
if args.zones:
    print('[+] The following zones exist on the device:')
    for zone in device.get_zones():
        print(f'[-] {zone["edit"]}')
        if "interface" in zone.keys():
            if isinstance(zone["interface"], list):
                child_interfaces = ", ".join(zone["interface"])
            else:
                child_interfaces = zone["interface"]
            print(f'     | interfaces {child_interfaces}')
    exit(0)

print(f'[+] Starting checks for levels: {",".join(args.levels)}')

if args.ids is not None:
    print(f'[+] Limiting to checks {", ".join(args.ids)}')

# Discover checks provided by the module
module.load_checks()

# Instantiate checkers
performed_checks = []

checkers = [check_class(device, display, verbose) for check_class in module.check_classes()]
for checker in checkers:
    if not checker.is_valid():
        continue

    if args.ids is not None and checker.get_id() not in args.ids:
        continue

    if checker.enabled and checker.is_level_applicable(args.levels):
        if checker.auto:
            checker.run()
        else:
            if quiet:
                checker.skip()
            else:
                if args.resume:
                    if checker.get_id() in cached_results.keys():
                        # There is a cached result for this check
                        checker.restore_from_cache(cached_results[checker.get_id()])
                    else:
                        # There is no cached result, we have to perform the step
                        checker.run()
                else:
                    checker.run()
        performed_checks.append(checker)

        # Save to cache
        cached_results[checker.get_id()] = {
            "result": checker.result,
            "message": checker.message,
            "question": checker.question,
            "question_context": checker.question_context,
            "answer": checker.answer,
        }

print('[+] Finished')
print('------------------------------------------------')
print('[+] Here is a summary:')

for performed_check in performed_checks:
    print(f'[{performed_check.get_id()}]\t[{performed_check.result}]\t{performed_check.title}')

# Save cache file
cache[filepath] = cached_results
cache_file = open(cache_file_path, "w")
json.dump(cache, cache_file)
cache_file.close()

# Export
if outputfile is not None:
    print('------------------------------------------------')
    print(f'[+] Exporting results in {outputfile}')
    outputfile = open(outputfile, "w+")
    outputfile.write("Check ID,Result,Check Title,Levels,Log\n")
    for performed_check in performed_checks:
        cleaned_message = performed_check.get_log().replace('"', '\'')
        levels = ",".join(str(x) for x in performed_check.levels)
        line = f'{performed_check.get_id()},{performed_check.result},{performed_check.title},"{levels}","{cleaned_message}"\n'
        outputfile.write(line)
    outputfile.close()
    print('[+] Finished')
