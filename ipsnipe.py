#!/usr/bin/env python3
"""
ipsnipe - A user-friendly CLI tool for machine reconnaissance
Author: hckerhub (X: @hckerhub)
Website: https://hackerhub.me
GitHub: https://github.com/hckerhub
Version: 3.1 - Portability & Installer Enhancement Edition

Complete reconnaissance revolution with unified Full Sniper Mode.
"""

import argparse
import sys
from ipsnipe import IPSnipeApp


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ipsnipe - Full Sniper Mode - Complete Reconnaissance Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ipsnipe.py                        # Full Sniper Mode (all 10 tools)
  python3 ipsnipe.py --enhanced             # Force enhanced mode (sudo)
  python3 ipsnipe.py --standard             # Force standard mode (no sudo)
  python3 ipsnipe.py --skip-disclaimer      # Skip disclaimer for automation

Full Sniper Mode runs all reconnaissance tools in optimized order:
• Phase 1: Network Discovery (aggressive nmap with high min-rate)
• Phase 2: DNS & Domain Intelligence  
• Phase 3: Web Application Analysis

For more information, visit: https://github.com/hckerhub
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='ipsnipe 3.1 (Portability & Installer Enhancement Edition)'
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
    # If no flags provided, sudo_mode remains None and will be handled after disclaimer
    
    # Create and run the application
    app = IPSnipeApp(skip_disclaimer=args.skip_disclaimer, sudo_mode=sudo_mode)
    app.run()


if __name__ == "__main__":
    main() 