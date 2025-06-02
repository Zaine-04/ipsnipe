#!/usr/bin/env python3
"""
ipsnipe - A user-friendly CLI tool for machine reconnaissance
Author: hckerhub (X: @hckerhub)
Website: https://hackerhub.me
GitHub: https://github.com/hckerhub
Version: 1.0.5

This is the refactored version with modular architecture.
"""

import argparse
import sys
from ipsnipe import IPSnipeApp


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ipsnipe - Advanced Machine Reconnaissance Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ipsnipe.py                        # Interactive mode
  python3 ipsnipe.py --enhanced             # Force enhanced mode (sudo)
  python3 ipsnipe.py --standard             # Force standard mode (no sudo)
  python3 ipsnipe.py --skip-disclaimer      # Skip disclaimer for automation

For more information, visit: https://github.com/hckerhub
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='ipsnipe 1.0.5 (Refactored)'
    )
    
    parser.add_argument(
        '--skip-disclaimer',
        action='store_true',
        help='Skip the ethical use disclaimer (for automated use - you still must use ethically!)'
    )
    
    # Sudo mode options
    sudo_group = parser.add_mutually_exclusive_group()
    sudo_group.add_argument(
        '--enhanced',
        action='store_true',
        help='Force Enhanced Mode (sudo) - enables SYN scans, OS detection, UDP scans'
    )
    sudo_group.add_argument(
        '--standard',
        action='store_true',
        help='Force Standard Mode (no sudo) - uses TCP connect scans only'
    )
    
    args = parser.parse_args()
    
    # Determine sudo mode preference
    sudo_mode = None
    if args.enhanced:
        sudo_mode = True
    elif args.standard:
        sudo_mode = False
    
    # Create and run the application
    app = IPSnipeApp(skip_disclaimer=args.skip_disclaimer, sudo_mode=sudo_mode)
    app.run()


if __name__ == "__main__":
    main() 