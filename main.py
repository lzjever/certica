#!/usr/bin/env python3
"""
Main entry point for Certica - CA Certificate Tool
"""
import sys
from certica.cli import cli


def main():
    """Main entry point"""
    # Always use Click CLI - it will handle help, commands, and UI mode
    try:
        cli()
    except SystemExit:
        # Click raises SystemExit for help/errors, which is normal
        pass


if __name__ == "__main__":
    main()

