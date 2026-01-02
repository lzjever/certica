#!/usr/bin/env python3
"""
Main entry point for Certica - CA Certificate Tool
"""
import sys
from certica.system_check import check_system_requirements
from certica.ui import CAUITool
from certica.cli import cli


def main():
    """Main entry point"""
    # If there are command line arguments, use CLI mode
    # Otherwise, use interactive UI mode
    if len(sys.argv) > 1:
        # Command line mode - click will handle help and errors
        # System check is handled in cli() function
        try:
            cli()
        except SystemExit:
            # Click raises SystemExit for help/errors, which is normal
            pass
    else:
        # Interactive UI mode - check system requirements first
        if not check_system_requirements():
            print("\nError: System requirements check failed.")
            print("Please install the missing tools before using Certica.")
            sys.exit(1)
        
        tool = CAUITool()
        try:
            tool.run()
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)


if __name__ == "__main__":
    main()

