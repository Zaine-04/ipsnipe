#!/usr/bin/env python3
"""
Configuration management for ipsnipe
Handles TOML loading and default configurations
"""

from pathlib import Path
from typing import Dict

try:
    # Try Python 3.11+ built-in tomllib first
    import tomllib
    def load_toml(file_path):
        with open(file_path, 'rb') as f:
            return tomllib.load(f)
except ImportError:
    try:
        # Fallback to external toml library
        import toml
        def load_toml(file_path):
            return toml.load(file_path)
    except ImportError:
        # If no TOML library available, provide a simple parser
        print("⚠️  No TOML library found. Using basic configuration parsing.")
        def load_toml(file_path):
            # Simple TOML-like parser for basic configs
            config = {}
            current_section = None
            
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        config[current_section] = {}
                    elif '=' in line and current_section:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        # Basic type conversion
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.isdigit():
                            value = int(value)
                        elif value.replace('.', '').isdigit():
                            value = float(value)
                        
                        config[current_section][key] = value
            
            return config


class ConfigManager:
    """Manages configuration loading and access"""
    
    @staticmethod
    def get_default_config() -> Dict:
        """Returns the minimal fallback configuration
        
        These are only basic defaults used when config.toml is missing or incomplete.
        ALL USER CONFIGURATION SHOULD BE DONE IN config.toml - NOT HERE!
        """
        return {
            'general': {
                'scan_timeout': 600,
                'default_threads': 50,
                'colorize_output': True,
                'verbose_logging': True
            },
            'wordlists': {
                'base_dir': '/usr/share/wordlists'
            },
            'nmap': {
                'quick_ports': '1000',
                'timing': 'T4'
            },
            'gobuster': {
                'threads': 50
            },
            'feroxbuster': {
                'threads': 50
            },
            'ffuf': {
                'threads': 40,
                'method': 'vhost'
            },
            'nikto': {
                'timeout': 300
            },
            'whatweb': {
                'aggression': 1
            },
            'theharvester': {
                'limit': 100
            },
            'dnsrecon': {
                'threads': 10
            },
            'output': {
                'colorize_output': True
            }
        }
    
    @staticmethod
    def load_config() -> Dict:
        """Load configuration from config.toml file"""
        config_file = Path("config.toml")
        default_config = ConfigManager.get_default_config()
        
        if config_file.exists():
            try:
                user_config = load_toml(config_file)
                # Merge user config with defaults
                for section, values in user_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values
                from ..ui.colors import Colors
                print(f"{Colors.GREEN}✅ Loaded configuration from config.toml{Colors.END}")
            except Exception as e:
                from ..ui.colors import Colors
                print(f"{Colors.YELLOW}⚠️  Error loading config.toml, using defaults: {e}{Colors.END}")
        
        return default_config 