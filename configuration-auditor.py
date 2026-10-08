#!/usr/bin/env python3
"""Small shim preserving the original script name while delegating
to the importable entry point `configuration_auditor.main`.
"""
from configuration_auditor import main


if __name__ == '__main__':
    main()
