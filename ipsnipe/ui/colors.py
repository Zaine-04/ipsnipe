#!/usr/bin/env python3
"""
Rich-powered display utilities for ipsnipe
Simplified color and formatting using Rich library
"""

from rich.console import Console
from rich.text import Text

# Global console instance for consistent styling
console = Console()

# Legacy Colors class for backward compatibility
class Colors:
    """Backward compatibility - now uses Rich internally"""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    PURPLE = ""
    CYAN = ""
    WHITE = ""
    BOLD = ""
    UNDERLINE = ""
    END = ""

# ASCII Art Banner (same as before)
BANNER_TEXT = r"""
 ___  ________  ________  ________   ___  ________  _______      
|\  \|\   __  \|\   ____\|\   ___  \|\  \|\   __  \|\  ___ \     
\ \  \ \  \|\  \ \  \___|\ \  \\ \  \ \  \ \  \|\  \ \   __/|    
 \ \  \ \   ____\ \_____  \ \  \\ \  \ \  \ \   ____\ \  \_|/__  
  \ \  \ \  \___|\|____|\  \ \  \\ \  \ \  \ \  \___|\ \  \_|\ \ 
   \ \__\ \__\     ____\_\  \ \__\\ \__\ \__\ \__\    \ \_______\
    \|__|\|__|    |\_________\|__| \|__|\|__|\|__|     \|_______|
                  \|_________|                                   

            ⚡ Advanced Machine Reconnaissance Framework v3.1 ⚡
    ════════════════════════════════════════════════════════
"""

def print_banner():
    """Print the ipsnipe banner with Rich styling"""
    banner = Text(BANNER_TEXT, style="cyan")
    console.print(banner)

# Convenience functions for common styled output
def print_success(message: str):
    """Print success message"""
    console.print(f"✅ {message}", style="green")

def print_error(message: str):
    """Print error message"""
    console.print(f"❌ {message}", style="red")

def print_warning(message: str):
    """Print warning message"""
    console.print(f"⚠️  {message}", style="yellow")

def print_info(message: str):
    """Print info message"""
    console.print(f"ℹ️  {message}", style="cyan")

def print_status(message: str, style: str = "white"):
    """Print status message with custom style"""
    console.print(message, style=style) 