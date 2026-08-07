"""Day 5: module entry point for the Assembler command-line interface.

Concept: make `python3 -m Assembler` the same front door as the CLI.
Design rules: defer all interface behavior to one testable `cli.main` function.
"""

from .cli import main

raise SystemExit(main())
