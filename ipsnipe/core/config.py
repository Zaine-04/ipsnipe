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
        """Returns the default configuration"""
        return {
            'general': {
                'scan_timeout': 300,
                'default_threads': 50,
                'colorize_output': True,
                'verbose_logging': True
            },
            'wordlists': {
                'base_dir': '/usr/share/wordlists',
                'common': '/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt',
                'small': '/usr/share/wordlists/dirb/common.txt',
                'medium': '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt',
                'big': '/usr/share/wordlists/dirb/big.txt',
                'custom': '/usr/share/seclists/Discovery/Web-Content/common.txt'
            },
            'nmap': {
                'quick_ports': '1000',
                'timing': 'T4',
                'version_intensity': '5',
                'enable_os_detection': True,
                'enable_version_detection': True,
                'enable_script_scan': True,
                'udp_ports': 200
            },
            'gobuster': {
                'extensions': 'php,html,txt,js,css,zip,tar,gz,bak,old',
                'threads': 50,
                'timeout': '10s',
                'follow_redirects': False,
                'include_length': True,
                'status_codes': '200,204,301,302,307,401,403'
            },
            'feroxbuster': {
                'extensions': 'php,html,txt,js,css,zip,tar,gz,bak,old',
                'threads': 50,
                'timeout': 10,
                'depth': 2,
                'wordlist_size': 'common'
            },
            'ffuf': {
                'extensions': '.php,.html,.txt,.js,.css,.zip,.tar,.gz,.bak,.old',
                'threads': 50,
                'timeout': 10,
                'match_codes': '200,204,301,302,307,401,403',
                'filter_size': ''
            },
            'nikto': {
                'format': 'txt',
                'timeout': 300,
                'max_scan_time': 300
            },
            'whatweb': {
                'verbosity': 'verbose',
                'aggression': 1
            },
            'theharvester': {
                'data_source': 'all',
                'limit': 100
            },
            'dnsrecon': {
                'record_types': 'std',
                'threads': 10
            },
            'output': {
                'max_line_length': 120,
                'truncate_long_lines': True,
                'highlight_important': True,
                'include_timestamps': True,
                'include_command_details': True,
                'include_execution_time': True,
                'include_file_sizes': True
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