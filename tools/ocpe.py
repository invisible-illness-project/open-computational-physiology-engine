#!/usr/bin/env python3
"""
OCPE Unified Command Line Interface
Provides single-point access to OCPE validation, governance, review tracking,
and simulation evaluation commands.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tools.review_tracker as review_tracker
import tools.validate_kb as validate_kb


def print_help():
    print("""
Open Computational Physiology Engine (OCPE) CLI

Usage:
  ocpe validate <asset>                         Run validation check on asset
  ocpe validate review <asset> [options]         Record a review event
  ocpe validate aggregate <asset>               Aggregate validation evidence
  ocpe validate challenge <asset> [options]     Record or update scientific challenge
  ocpe validate authorize <asset> --use <use>   Check downstream usage authorization
  ocpe validate explain <asset>                 Display human-readable validation report
  ocpe validate kb [--record]                   Validate Knowledge Base YAML files

Direct Subcommands:
  ocpe review <asset> [options]                 Record review event
  ocpe aggregate <asset>                        Aggregate validation evidence
  ocpe challenge <asset> [options]              Record scientific challenge
  ocpe authorize <asset> --use <use>            Check downstream authorization
  ocpe explain <asset>                          Display validation provenance report
  ocpe history <asset>                          Show chronological review history
  ocpe summary [<directory>]                    Display directory-wide review coverage
  ocpe migrate [<target>]                       Migrate v1 manifests to v2 schema
""")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help", "help"}:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "validate":
        if len(sys.argv) == 2:
            print_help()
            sys.exit(1)

        sub = sys.argv[2]
        if sub == "kb":
            # Pass remaining args to validate_kb main
            sys.argv = [sys.argv[0]] + sys.argv[3:]
            validate_kb.main()
        elif sub in {"review", "record", "aggregate", "challenge", "authorize", "explain", "history", "summary", "migrate"}:
            # Reframe args: ocpe validate review asset -> review_tracker.py review asset
            sys.argv = [sys.argv[0], sub] + sys.argv[3:]
            review_tracker.main()
        else:
            # ocpe validate <asset>
            sys.argv = [sys.argv[0], "validate"] + sys.argv[2:]
            review_tracker.main()

    elif cmd in {"review", "record", "aggregate", "challenge", "authorize", "explain", "history", "summary", "migrate"}:
        sys.argv = [sys.argv[0]] + sys.argv[1:]
        review_tracker.main()

    else:
        print(f"Unknown command '{cmd}'")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
