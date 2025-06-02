#!/usr/bin/env python3
"""
Color utilities for ipsnipe terminal output
ANSI color codes and formatting
"""


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# ASCII Art Banner
BANNER = r"""
 ___  ________  ________  ________   ___  ________  _______      
|\  \|\   __  \|\   ____\|\   ___  \|\  \|\   __  \|\  ___ \     
\ \  \ \  \|\  \ \  \___|\ \  \\ \  \ \  \ \  \|\  \ \   __/|    
 \ \  \ \   ____\ \_____  \ \  \\ \  \ \  \ \   ____\ \  \_|/__  
  \ \  \ \  \___|\|____|\  \ \  \\ \  \ \  \ \  \___|\ \  \_|\ \ 
   \ \__\ \__\     ____\_\  \ \__\\ \__\ \__\ \__\    \ \_______\
    \|__|\|__|    |\_________\|__| \|__|\|__|\|__|     \|_______|
                  \|_________|                                   

    ⚡ Advanced Machine Reconnaissance Framework v1.0.5 ⚡
    ════════════════════════════════════════════════════════
"""


def print_banner():
    """Print the ipsnipe banner"""
    print(f"{Colors.CYAN}{BANNER}{Colors.END}") 