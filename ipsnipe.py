#!/usr/bin/env python3
"""
ipsnipe - Advanced Machine Reconnaissance Framework

Version: 3.2 - Wordlist Management & Configuration Stability Edition
Author: hckerhub
Website: https://hackerhub.me
GitHub: https://github.com/hckerhub

A comprehensive reconnaissance tool for HTB/CTF environments
with intelligent wordlist management and context-aware scanning.
"""

import argparse
import sys
from ipsnipe import IPSnipeApp
import textwrap


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ipsnipe - Advanced Machine Reconnaissance Framework',
        epilog=textwrap.dedent('''
        Examples:
          python3 ipsnipe.py 10.10.10.100             # Basic reconnaissance
          python3 ipsnipe.py 10.10.10.100 -p 22,80,443 # Custom ports
          python3 ipsnipe.py 10.10.10.100 -p 1-1000    # Port range
          python3 ipsnipe.py -h                         # Show this help
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('target_ip', nargs='?', help='Target IP address')
    parser.add_argument('-p', '--ports', help='Ports to scan (e.g., 22,80,443 or 1-1000)')
    parser.add_argument('-e', '--enhanced', action='store_true', help='Enable enhanced mode')
    parser.add_argument('--skip-disclaimer', action='store_true', help='Skip disclaimer')
    parser.add_argument('--sudo', action='store_true', help='Force sudo mode')
    parser.add_argument('--no-sudo', action='store_true', help='Force non-sudo mode')
    parser.add_argument('--version', action='version', 
                       version='ipsnipe 3.2 (Wordlist Management & Configuration Stability Edition)')
    
    args = parser.parse_args()
    
    # Determine sudo mode preference
    sudo_mode = None
    if args.enhanced:
        sudo_mode = True
    elif args.sudo:
        sudo_mode = True
    elif args.no_sudo:
        sudo_mode = False
    # If no flags provided, sudo_mode remains None and will be handled after disclaimer
    
    # Create and run the application
    app = IPSnipeApp(skip_disclaimer=args.skip_disclaimer, sudo_mode=sudo_mode)
    app.run()


if __name__ == "__main__":
    main() 