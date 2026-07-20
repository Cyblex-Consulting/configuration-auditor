# Configuration Auditor

A generic, modular CLI tool to audit a device configuration against security
benchmarks (CIS, Cyblex, ...).

The tool is split into a vendor-agnostic **core** and pluggable **modules**.
Each module knows how to parse one vendor's configuration and ships its own set
of checks. Two modules are provided:

- `fortigate` — FortiGate / FortiManager (full implementation, CIS + Cyblex benchmarks).
- `pfsense` — pfSense (skeleton only, not yet implemented).

## Architecture

```
configuration-auditor.py     # generic entrypoint (--module required)
core/                        # vendor-agnostic building blocks
  checker.py                 #   Checker base class (all checks subclass it)
  display.py                 #   output / prompt helper
  device.py                  #   Device base class (parsed config wrapper)
  module.py                  #   Module base class (vendor integration point)
  registry.py                #   discovers/loads modules by name
modules/
  fortigate/                 # FortiGate module (self-contained)
    module.py                #   parsing (fortios_xutils) + check discovery
    device.py                #   FortigateDevice (config accessors)
    fortiguard.py            #   FortiGuard category/app ID lookup
    libs/FortigateAppControlID   # git submodule (App Control CSVs)
    checks/<benchmark>/      #   the actual checks
  pfsense/                   # pfSense module (skeleton)
    module.py
    device.py
    checks/
```

The entrypoint never imports vendor code directly. It loads the requested
module through `core/registry.py`, asks it to parse the config into a `Device`,
then runs the checks the module exposes.

## Setup

FortiGate parsing is done with https://github.com/ssato/fortios-xutils :

```
pip install fortios_xutils
```

The FortiGate module ships an App Control ID database as a git submodule:

```
git submodule update --init
```

**Note:** FortiGate parsing may fail if the config contains non utf-8
characters or hits a known parser bug. The `--autofix` flag works around both
(it may remove some non standard characters).

## Running

```
usage: configuration-auditor.py [-h] -m {fortigate,pfsense} [-q] [-v] [-j]
                                [-o OUTPUT] [-l LEVELS [LEVELS ...]]
                                [-i IDS [IDS ...]] [-c] [-w WAN [WAN ...]]
                                [--interfaces] [--zones] [--autofix] config

Configuration Auditor - apply a security benchmark to a device configuration file.

positional arguments:
  config                Configuration file exported from the device

options:
  -h, --help            show this help message and exit
  -m, --module {fortigate,pfsense}
                        Configuration module to use (required)
  -q, --quiet           Not interactive: ignore manual steps
  -v, --verbose         Increase verbosity
  -j, --json            Input file is json already parsed by the module
  -o OUTPUT, --output OUTPUT
                        Output CSV File
  -l LEVELS [LEVELS ...], --levels LEVELS [LEVELS ...]
                        Levels to check. (default: 1)
  -i IDS [IDS ...], --ids IDS [IDS ...]
                        Checks id to perform. (default: all if applicable)
  -c, --resume          Resume an audit that was already started. Automatic
                        items are re-checked but manually set values are
                        retrieved from cache.
  -w WAN [WAN ...], --wan WAN [WAN ...]
                        List of wan interfaces separated by spaces
  --interfaces          Show list of interfaces and exit
  --zones               Show list of zones and exit
  --autofix             Automatically try to fix errors in input file
```

Example:

```
python3 configuration-auditor.py -m fortigate -q -o results.csv -l 1 2 -w port1 port2 --autofix firewall.conf
```

The `--module` / `-m` flag is **required**.

Results are cached per module in `~/.cache/configuration-auditor-<module>.json`,
keyed by the config file path. By default a rerun overwrites the cache; add
`-c` / `--resume` to reload previous **manual** answers (automatic checks always
rerun).

## Adding a module

Create a sub-package under `modules/<vendor>/` with:

- `__init__.py` exposing a `get_module(display, verbose)` factory.
- `module.py` with a `Module` subclass implementing `parse()` (and optionally
  `parse_json()`), setting `name`, `description`, `device_class`, and
  implementing `load_checks()`.
- `device.py` with a `Device` subclass implementing `get_config()` and any
  vendor accessors your checks need.
- `checks/` with the discovery `__init__.py` pattern (see below) and one
  sub-folder per benchmark.

The registry auto-discovers any sub-package of `modules/` that exposes
`get_module()`; it then appears automatically in `--module` choices.

## Adding checks

Create a sub-folder in a module's `checks/` directory (one per benchmark). Each
check is an independent python file whose class subclasses `Checker`.

**Check discovery is by `Checker.__subclasses__()`, not by scanning files.** A
check only runs if its module has been imported. Each `checks/` package and each
benchmark sub-folder contains an `__init__.py` that imports its contents; when
adding a new benchmark folder, copy an existing `__init__.py` into it.

Mandatory subclass variables:

- `self.id`: Reference for the requirement (in the benchmark)
- `self.title`: Title for the requirement
- `self.levels`: List of levels applicable for the requirement
- `self.auto`: True if the check does not need the operator to review and assess
- `self.benchmark_version`: The benchmark version used to implement the check
- `self.benchmark_author`: The benchmark author

Implement `do_check()`, which returns:
- `True` if the check passed
- `False` if the check failed
- `None` if the check was not performed (marked `SKIP`)

Message helpers (shown in verbose mode / logs):
- `self.set_message(text)` — set the message (overwrites).
- `self.add_message(text)` — append a line to the message.

Manual-check helpers:
- `self.ask(question)` — display a question, return the user's input.
- `self.add_question_context(string)` — append a line to the question context.
- `self.ask_if_correct()` — display the context and ask the user to validate.

Generic helpers (in `core/checker.py`):
- `self.get_config(chapter=None)` — a single config block, or the full config.
- `self.is_ip(param)` — checks IP format.
- `self.is_fqdn(param)` — checks FQDN format.
- `self.get_wan_interfaces()` — WAN interfaces (from `--wan` or prompted).
- `self.device` — the vendor `Device` for vendor-specific accessors.
  (`self.firewall` remains as a backward-compatible alias.)

FortiGate `Device` accessors available via `self.device` (or `self.firewall`):
`get_interfaces()`, `get_zones()`, `get_policies(...)`, `get_ips_sensors(...)`,
`get_av_profiles(...)`, `get_dnsfilter_profiles(...)`,
`get_appcontrol_profiles(...)`,
`get_service_groups_containing_protocols(...)`, and `fortiguard` lookups.

### Example

A single automatic check (from the FortiGate module):

```python
from core.checker import Checker

class Check_Example_Auto(Checker):

    def __init__(self, device, display, verbose=False):
        super().__init__(device, display, verbose)
        self.id = "1.1.2"
        self.title = "Example Auto Check"
        self.levels = [1, 2]
        self.auto = True
        self.enabled = False  # Remove this line to enable
        self.benchmark_version = "v1.1.0"
        self.benchmark_author = "Example Org."

    def do_check(self):
        config_system_dns = self.get_config("system dns")

        if "primary" not in config_system_dns.keys():
            self.set_message('No primary DNS configured')
            return False

        if not self.is_ip(config_system_dns["primary"]):
            self.set_message(f'{config_system_dns["primary"]} is not a valid IP')
            return False

        return True
```
