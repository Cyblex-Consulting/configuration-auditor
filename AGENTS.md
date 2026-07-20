# AGENTS.md

Configuration Auditor: a generic CLI tool that audits an exported device config
against security benchmarks (CIS, Cyblex). Vendor-agnostic core + pluggable
vendor modules. Plain Python 3, no build system, no test suite, no linter config.

## Run

```
python3 configuration-auditor.py -m <module> [flags] <config>
# example: python3 configuration-auditor.py -m fortigate -q -o results.csv -l 1 2 -w port1 port2 --autofix firewall.conf
```

`-m/--module` is REQUIRED (choices are auto-discovered from `modules/`: currently
`fortigate`, `pfsense`). Must be run from the repo root — imports are flat-ish
package imports (`from core.checker import Checker`, `import modules.fortigate...`)
relying on CWD being the repo root.

Vendor-specific runtime paths (FortiGate module):
- `tmp/` — scratch dir for parsing; the config is copied here before parsing.
  The FortiGate module auto-creates it if missing (gitignored).
- `modules/fortigate/libs/FortigateAppControlID/{Categories,Applications}.csv` —
  loaded at startup by `fortiguard.py` when the FortiGate device is built.

## Setup

- `pip install fortios_xutils` (the FortiGate config parser; imported by the
  fortigate module, no requirements file).
- `git submodule update --init` — `modules/fortigate/libs/FortigateAppControlID`
  is a git submodule; without it the FortiGate module fails loading the CSVs.

## Layout

- `configuration-auditor.py` — generic entrypoint (argparse, module loading,
  cache, run loop, CSV export). Contains NO vendor code.
- `core/` — vendor-agnostic building blocks:
  - `checker.py` — `Checker` base class. All checks subclass it. (`self.device`
    is the parsed config; `self.firewall` is a backward-compat alias.)
  - `display.py` — `Display` output/prompt helper.
  - `device.py` — `Device` base class; vendor adapters subclass it.
  - `module.py` — `Module` base class; the entrypoint's single integration point.
  - `registry.py` — discovers/loads modules by name from `modules/`.
- `modules/<vendor>/` — self-contained vendor module. Must expose
  `get_module(display, verbose)` in its `__init__.py`.
  - `modules/fortigate/` — full impl: `module.py` (parsing via fortios_xutils +
    check discovery), `device.py` (`FortigateDevice`), `fortiguard.py`,
    `checks/<benchmark>/check-*.py`.
  - `modules/pfsense/` — SKELETON only: `module.py`/`device.py` raise
    `NotImplementedError`; parsing and real checks are TODO.

## Module discovery (non-obvious)

- `core/registry.py` lists any sub-package of `modules/` (not starting with `__`)
  and instantiates it via its `get_module()` factory. New module folders appear
  automatically in `--module` choices.

## Check discovery (non-obvious)

- Checks are found via `Checker.__subclasses__()`, NOT by scanning files. A check
  only runs if its module is imported. The entrypoint calls `module.load_checks()`
  which imports the module's `checks` package.
- `modules/<vendor>/checks/__init__.py` imports each benchmark subfolder; each
  subfolder's `__init__.py` imports every `.py` in it (using `__name__` for the
  package prefix). When adding a new benchmark folder, copy an existing
  `__init__.py` into it or checks won't load.
- Check files import `from core.checker import Checker`.

## Adding a module

Create `modules/<vendor>/` with `__init__.py` (a `get_module(display, verbose)`
factory), `module.py` (a `Module` subclass: set `name`/`description`/
`device_class`, implement `parse()` and `load_checks()`), `device.py` (a `Device`
subclass implementing `get_config()`), and a `checks/` package using the
discovery `__init__.py` pattern. See `modules/pfsense/` for the minimal skeleton.

## Adding a check

Subclass `Checker` in `modules/<vendor>/checks/<benchmark>/check-*.py`. Required
attributes in `__init__`: `self.id`, `self.title`, `self.levels` (list of ints),
`self.auto` (bool), `self.benchmark_version`, `self.benchmark_author`. Implement
`do_check()` returning `True`=pass, `False`=fail, `None`=SKIP. Constructor sig is
`(self, device, display, verbose=False)`. See `modules/fortigate/checks/examples/`
and README.md "Adding checks".

## Gotchas

- Cache lives at `~/.cache/configuration-auditor-<module>.json`, keyed by config
  file path (one cache file per module). Without `-c/--resume` a rerun overwrites
  it; only manual answers are restored on resume, auto checks always rerun.
- The FortiGate parser chokes on non-UTF-8 chars and on a known `set config read`
  bug; `--autofix` mutates the temp copy to work around both.
- Parsed FortiGate config blocks look like `{"config": "<chapter>", "edits": [...]}`;
  some fields can be a string or a list (e.g. policy comments) — handle both.
- `-l/--levels` uses nargs='+'; put the positional `config` before `-l` (e.g.
  `... config.conf -l 1 2`) or the levels list will swallow the positional.
