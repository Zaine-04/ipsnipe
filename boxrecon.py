#!/usr/bin/env python3
"""
BoxRecon - A user-friendly CLI tool for machine reconnaissance
Author: hckerhub (X: @hckerhub)
Website: https://hackerhub.me
GitHub: https://github.com/hckerhub
Version: 1.0.0
"""

import os
import sys
import subprocess
import argparse
import ipaddress
import json
import datetime
import re
import textwrap
from pathlib import Path
from typing import Dict, List, Optional
import threading
import time

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

# ASCII Art Banner
BANNER = """
██████╗  ██████╗ ██╗  ██╗██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗╚██╗██╔╝██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
██████╔╝██║   ██║ ╚███╔╝ ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██╗██║   ██║ ██╔██╗ ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██╔╝ ██╗██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

    ⚡ Advanced Machine Reconnaissance Framework ⚡
    ═══════════════════════════════════════════════
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

class BoxRecon:
    def __init__(self, skip_disclaimer=False):
        self.target_ip = None
        self.output_dir = None
        self.results = {}
        self.config = self.load_config()
        self.skip_disclaimer = skip_disclaimer
    
    def load_config(self) -> Dict:
        """Load configuration from config.toml file"""
        config_file = Path("config.toml")
        
        # Default configuration
        default_config = {
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
                'custom': '/usr/share/wordlists/custom/htb-common.txt'
            },
            'nmap': {
                'quick_ports': '1000',
                'timing': 'T4',
                'version_intensity': '5',
                'enable_os_detection': True,
                'enable_version_detection': True,
                'enable_script_scan': True
            },
            'gobuster': {
                'extensions': 'php,html,txt,js,css,zip,tar,gz,bak,old',
                'threads': 50,
                'timeout': '10s',
                'follow_redirects': False,
                'include_length': True,
                'status_codes': '200,204,301,302,307,401,403'
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
        
        if config_file.exists():
            try:
                user_config = load_toml(config_file)
                # Merge user config with defaults
                for section, values in user_config.items():
                    if section in default_config:
                        default_config[section].update(values)
                    else:
                        default_config[section] = values
                print(f"{Colors.GREEN}✅ Loaded configuration from config.toml{Colors.END}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Error loading config.toml, using defaults: {e}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  config.toml not found, using default configuration{Colors.END}")
        
        return default_config
    
    def format_output_content(self, content: str, scan_type: str) -> str:
        """Format scan output for better readability"""
        if not content.strip():
            return "No output generated."
        
        lines = content.split('\n')
        formatted_lines = []
        max_length = self.config['output']['max_line_length']
        
        for line in lines:
            # Skip empty lines at the beginning
            if not formatted_lines and not line.strip():
                continue
                
            # Truncate very long lines if configured
            if self.config['output']['truncate_long_lines'] and len(line) > max_length:
                line = line[:max_length-3] + "..."
            
            # Highlight important findings based on scan type
            if self.config['output']['highlight_important']:
                line = self.highlight_important_findings(line, scan_type)
            
            formatted_lines.append(line)
        
        # Remove trailing empty lines
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()
        
        return '\n'.join(formatted_lines)
    
    def highlight_important_findings(self, line: str, scan_type: str) -> str:
        """Highlight important findings in scan output"""
        if scan_type == "nmap":
            # Highlight open ports
            if re.search(r'\d+/tcp\s+open', line):
                return f"🔓 {line}"
            elif re.search(r'\d+/udp\s+open', line):
                return f"🔓 {line}"
            elif "Nmap scan report" in line:
                return f"🎯 {line}"
        
        elif scan_type in ["gobuster", "feroxbuster", "ffuf"]:
            # Highlight discovered directories/files
            if re.search(r'(Status:\s*200|200\s+)', line):
                return f"📁 {line}"
            elif re.search(r'(Status:\s*30[1-8]|30[1-8]\s+)', line):
                return f"↪️  {line}"
            elif re.search(r'(Status:\s*40[1-4]|40[1-4]\s+)', line):
                return f"🔒 {line}"
        
        elif scan_type == "nikto":
            # Highlight vulnerabilities
            if any(keyword in line.lower() for keyword in ['vulnerability', 'exploit', 'cve-', 'critical', 'high']):
                return f"⚠️  {line}"
            elif any(keyword in line.lower() for keyword in ['info', 'disclosure', 'version']):
                return f"ℹ️  {line}"
        
        elif scan_type == "whatweb":
            # Highlight technology stack
            if any(keyword in line.lower() for keyword in ['server:', 'powered by', 'framework', 'cms']):
                return f"🔧 {line}"
        
        elif scan_type == "theharvester":
            # Highlight emails and subdomains
            if '@' in line:
                return f"📧 {line}"
            elif any(keyword in line.lower() for keyword in ['subdomain', 'host']):
                return f"🌐 {line}"
        
        elif scan_type == "dnsrecon":
            # Highlight DNS records
            if any(record in line.upper() for record in ['A ', 'AAAA ', 'CNAME ', 'MX ', 'NS ', 'TXT ']):
                return f"🔍 {line}"
        
        return line
    
    def get_wordlist_path(self, wordlist_type: str) -> str:
        """Get wordlist path from configuration with fallbacks"""
        wordlist_path = self.config['wordlists'].get(wordlist_type)
        
        if wordlist_path and Path(wordlist_path).exists():
            return wordlist_path
        
        # Fallback options
        fallbacks = {
            'common': [
                '/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt',
                '/usr/share/wordlists/dirb/common.txt',
                '/usr/share/seclists/Discovery/Web-Content/common.txt'
            ],
            'small': [
                '/usr/share/wordlists/dirb/common.txt',
                '/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt'
            ],
            'big': [
                '/usr/share/wordlists/dirb/big.txt',
                '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt'
            ]
        }
        
        for fallback in fallbacks.get(wordlist_type, []):
            if Path(fallback).exists():
                print(f"{Colors.YELLOW}📝 Using fallback wordlist: {fallback}{Colors.END}")
                return fallback
        
        # Last resort - create a minimal wordlist
        print(f"{Colors.RED}⚠️  No wordlist found for {wordlist_type}, using minimal built-in list{Colors.END}")
        return self.create_minimal_wordlist()
    
    def create_minimal_wordlist(self) -> str:
        """Create a minimal wordlist for HTB machines"""
        minimal_words = [
            'admin', 'administrator', 'login', 'dashboard', 'panel', 'config',
            'backup', 'uploads', 'files', 'images', 'css', 'js', 'api',
            'test', 'dev', 'development', 'staging', 'tmp', 'temp',
            'index.php', 'admin.php', 'login.php', 'config.php',
            'robots.txt', '.htaccess', 'sitemap.xml'
        ]
        
        wordlist_path = Path(self.output_dir) / 'minimal_wordlist.txt'
        with open(wordlist_path, 'w') as f:
            f.write('\n'.join(minimal_words))
        
        return str(wordlist_path)
        
    def show_disclaimer(self):
        """Display ethical use disclaimer"""
        print(f"{Colors.RED}{'=' * 80}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}                           ⚠️  ETHICAL USE DISCLAIMER ⚠️{Colors.END}")
        print(f"{Colors.RED}{'=' * 80}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}BoxRecon is designed for AUTHORIZED security testing and educational purposes only.{Colors.END}\n")
        
        print(f"{Colors.WHITE}By using this tool, you acknowledge and agree that:{Colors.END}")
        print(f"{Colors.CYAN}  • You will ONLY use this tool on systems you own or have explicit permission to test{Colors.END}")
        print(f"{Colors.CYAN}  • You will comply with all applicable local, state, and federal laws{Colors.END}")
        print(f"{Colors.CYAN}  • You understand that unauthorized access to computer systems is illegal{Colors.END}")
        print(f"{Colors.CYAN}  • You will use this tool responsibly and ethically{Colors.END}\n")
        
        print(f"{Colors.RED}The author (hckerhub) is NOT responsible for:{Colors.END}")
        print(f"{Colors.WHITE}  • Any damages caused to personal property or systems{Colors.END}")
        print(f"{Colors.WHITE}  • Any legal consequences resulting from misuse of this tool{Colors.END}")
        print(f"{Colors.WHITE}  • Any unauthorized access or illegal activities{Colors.END}")
        print(f"{Colors.WHITE}  • Any data loss or system compromise{Colors.END}\n")
        
        print(f"{Colors.GREEN}Legitimate use cases include:{Colors.END}")
        print(f"{Colors.WHITE}  • Penetration testing with proper authorization{Colors.END}")
        print(f"{Colors.WHITE}  • Security research on your own systems{Colors.END}")
        print(f"{Colors.WHITE}  • Educational purposes in controlled environments{Colors.END}")
        print(f"{Colors.WHITE}  • Bug bounty programs with explicit scope{Colors.END}")
        print(f"{Colors.WHITE}  • Capture The Flag (CTF) competitions{Colors.END}\n")
        
        print(f"{Colors.RED}{'=' * 80}{Colors.END}")
        
        while True:
            response = input(f"{Colors.YELLOW}Do you agree to use this tool ethically and legally? (yes/no): {Colors.END}").strip().lower()
            if response in ['yes', 'y']:
                print(f"{Colors.GREEN}✅ Ethical use agreement accepted. Proceeding...{Colors.END}\n")
                break
            elif response in ['no', 'n']:
                print(f"{Colors.RED}❌ Ethical use agreement declined. Exiting...{Colors.END}")
                sys.exit(0)
            else:
                print(f"{Colors.RED}Please enter 'yes' or 'no'{Colors.END}")

    def print_banner(self):
        """Display the BoxRecon banner"""
        print(f"{Colors.CYAN}{BANNER}{Colors.END}")
        print(f"{Colors.YELLOW}Welcome to BoxRecon - Your Advanced Reconnaissance Framework!{Colors.END}")
        print(f"{Colors.BLUE}Created by hckerhub | {Colors.CYAN}https://hackerhub.me{Colors.END}")
        print(f"{Colors.PURPLE}Support the project: {Colors.YELLOW}https://buymeacoffee.com/hckerhub{Colors.END}\n")
    
    def validate_ip(self, ip_string: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
    
    def get_target_ip(self) -> str:
        """Get and validate target IP address from user"""
        while True:
            ip = input(f"{Colors.CYAN}🎯 Enter target IP address: {Colors.END}").strip()
            if self.validate_ip(ip):
                print(f"{Colors.GREEN}✅ Valid IP address: {ip}{Colors.END}")
                return ip
            else:
                print(f"{Colors.RED}❌ Invalid IP address format. Please try again.{Colors.END}")
    
    def create_output_directory(self, ip: str) -> str:
        """Create output directory for results"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"boxrecon_{ip}_{timestamp}"
        output_dir = Path(dir_name)
        output_dir.mkdir(exist_ok=True)
        print(f"{Colors.GREEN}📁 Created output directory: {dir_name}{Colors.END}")
        return str(output_dir)
    
    def show_attack_menu(self) -> List[str]:
        """Display attack options and get user selection"""
        attacks = {
            '1': 'nmap_quick',
            '2': 'nmap_full',
            '3': 'nmap_udp',
            '4': 'gobuster_common',
            '5': 'gobuster_big',
            '6': 'feroxbuster',
            '7': 'ffuf',
            '8': 'nikto',
            '9': 'whatweb',
            '10': 'theharvester',
            '11': 'dnsrecon',
            '12': 'all_attacks'
        }
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Available Reconnaissance Options:{Colors.END}")
        print(f"{Colors.YELLOW}1.{Colors.END} Quick Nmap Scan (Top 1000 TCP ports)")
        print(f"{Colors.YELLOW}2.{Colors.END} Full Nmap Scan (All TCP ports)")
        print(f"{Colors.YELLOW}3.{Colors.END} Nmap UDP Scan (Top 200 UDP ports)")
        print(f"{Colors.YELLOW}4.{Colors.END} Gobuster - Common wordlist")
        print(f"{Colors.YELLOW}5.{Colors.END} Gobuster - Big wordlist")
        print(f"{Colors.YELLOW}6.{Colors.END} Feroxbuster - Fast directory enumeration")
        print(f"{Colors.YELLOW}7.{Colors.END} ffuf - Fast web fuzzer")
        print(f"{Colors.YELLOW}8.{Colors.END} Nikto Web Scanner")
        print(f"{Colors.YELLOW}9.{Colors.END} WhatWeb Technology Detection")
        print(f"{Colors.YELLOW}10.{Colors.END} theHarvester - Email/subdomain gathering")
        print(f"{Colors.YELLOW}11.{Colors.END} DNSrecon - DNS enumeration")
        print(f"{Colors.YELLOW}12.{Colors.END} Run All Attacks")
        print(f"{Colors.YELLOW}0.{Colors.END} Custom Selection (comma-separated)")
        
        while True:
            choice = input(f"\n{Colors.CYAN}🎯 Select attack options (e.g., 1,3,5 or 7 for all): {Colors.END}").strip()
            
            if choice == '12':
                return list(attacks.values())[:-1]  # All except 'all_attacks'
            elif choice == '0':
                custom = input(f"{Colors.CYAN}Enter custom selection (1,2,3...): {Colors.END}").strip()
                selected = []
                for num in custom.split(','):
                    num = num.strip()
                    if num in attacks and num != '12':
                        selected.append(attacks[num])
                if selected:
                    return selected
                else:
                    print(f"{Colors.RED}❌ Invalid selection. Please try again.{Colors.END}")
            else:
                selected = []
                for num in choice.split(','):
                    num = num.strip()
                    if num in attacks and num != '12':
                        selected.append(attacks[num])
                if selected:
                    return selected
                else:
                    print(f"{Colors.RED}❌ Invalid selection. Please try again.{Colors.END}")
    
    def run_command(self, command: List[str], output_file: str, description: str, scan_type: str = "generic") -> Dict:
        """Execute a command and save output with improved formatting"""
        timeout = self.config['general']['scan_timeout']
        print(f"{Colors.YELLOW}🔄 Running: {description}... (timeout: {timeout}s){Colors.END}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Format the output content
            formatted_stdout = self.format_output_content(result.stdout, scan_type)
            formatted_stderr = self.format_output_content(result.stderr, scan_type) if result.stderr else ""
            
            # Save output to file with better formatting
            output_path = Path(self.output_dir) / output_file
            file_size = 0
            
            with open(output_path, 'w') as f:
                # Header section
                f.write("=" * 80 + "\n")
                f.write(f"BoxRecon Scan Report - {description}\n")
                f.write("=" * 80 + "\n\n")
                
                if self.config['output']['include_command_details']:
                    f.write(f"Command: {' '.join(command)}\n")
                    f.write(f"Target: {self.target_ip}\n")
                
                if self.config['output']['include_timestamps']:
                    f.write(f"Start Time: {datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"End Time: {datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                if self.config['output']['include_execution_time']:
                    f.write(f"Execution Time: {execution_time:.2f} seconds\n")
                
                f.write(f"Return Code: {result.returncode}\n")
                f.write(f"Status: {'SUCCESS' if result.returncode == 0 else 'FAILED'}\n")
                f.write("\n" + "=" * 80 + "\n\n")
                
                # Main output section
                if formatted_stdout:
                    f.write("SCAN RESULTS:\n")
                    f.write("-" * 40 + "\n")
                    f.write(formatted_stdout)
                    f.write("\n\n")
                else:
                    f.write("No scan results generated.\n\n")
                
                # Error section (if any)
                if formatted_stderr:
                    f.write("ERRORS/WARNINGS:\n")
                    f.write("-" * 40 + "\n")
                    f.write(formatted_stderr)
                    f.write("\n\n")
                
                # Footer
                f.write("=" * 80 + "\n")
                f.write(f"End of {description} Report\n")
                f.write("=" * 80 + "\n")
            
            # Get file size
            file_size = output_path.stat().st_size
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {description} completed successfully ({execution_time:.1f}s, {file_size} bytes){Colors.END}")
                return {
                    'status': 'success',
                    'output_file': str(output_path),
                    'execution_time': execution_time,
                    'file_size': file_size,
                    'return_code': result.returncode
                }
            else:
                print(f"{Colors.RED}❌ {description} failed with return code {result.returncode} ({execution_time:.1f}s){Colors.END}")
                return {
                    'status': 'failed',
                    'output_file': str(output_path),
                    'return_code': result.returncode,
                    'execution_time': execution_time,
                    'file_size': file_size
                }
                
        except subprocess.TimeoutExpired:
            timeout_mins = timeout // 60
            print(f"{Colors.RED}⏰ {description} timed out after {timeout_mins} minutes{Colors.END}")
            
            # Create timeout report
            output_path = Path(self.output_dir) / output_file
            with open(output_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write(f"BoxRecon Scan Report - {description} (TIMEOUT)\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Command: {' '.join(command)}\n")
                f.write(f"Target: {self.target_ip}\n")
                f.write(f"Status: TIMEOUT after {timeout} seconds\n")
                f.write(f"Timeout Limit: {timeout_mins} minutes\n\n")
                f.write("The scan was terminated due to timeout.\n")
                f.write("Consider:\n")
                f.write("- Increasing timeout in config.toml\n")
                f.write("- Using a smaller wordlist\n")
                f.write("- Reducing scan scope\n")
            
            return {
                'status': 'timeout', 
                'output_file': str(output_path),
                'timeout_duration': timeout
            }
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Command not found. Please ensure required tools are installed.{Colors.END}")
            return {'status': 'not_found', 'output_file': output_file}
        except Exception as e:
            print(f"{Colors.RED}❌ Error running {description}: {str(e)}{Colors.END}")
            return {'status': 'error', 'output_file': output_file, 'error': str(e)}
    
    def nmap_quick_scan(self) -> Dict:
        """Run quick Nmap scan using configuration"""
        nmap_config = self.config['nmap']
        command = ['nmap', '-sS']
        
        if nmap_config['enable_version_detection']:
            command.extend(['-sV', '--version-intensity', str(nmap_config['version_intensity'])])
        
        if nmap_config['enable_os_detection']:
            command.append('-O')
        
        command.extend([
            '--top-ports', str(nmap_config['quick_ports']),
            f'-{nmap_config["timing"]}',
            self.target_ip
        ])
        
        return self.run_command(command, 'nmap_quick.txt', 'Nmap Quick Scan', 'nmap')
    
    def nmap_full_scan(self) -> Dict:
        """Run full Nmap scan using configuration"""
        nmap_config = self.config['nmap']
        command = ['nmap', '-sS']
        
        if nmap_config['enable_version_detection']:
            command.extend(['-sV', '--version-intensity', '9'])
        
        if nmap_config['enable_os_detection']:
            command.append('-O')
        
        command.extend(['-p-', f'-{nmap_config["timing"]}'])
        
        if nmap_config['enable_script_scan']:
            command.extend(['--script=default,vuln'])
        
        command.append(self.target_ip)
        
        return self.run_command(command, 'nmap_full.txt', 'Nmap Full Scan', 'nmap')
    
    def nmap_udp_scan(self) -> Dict:
        """Run UDP Nmap scan using configuration"""
        nmap_config = self.config['nmap']
        command = ['nmap', '-sU']
        
        command.extend([
            '--top-ports', str(nmap_config['udp_ports']),
            f'-{nmap_config["timing"]}',
            self.target_ip
        ])
        
        return self.run_command(command, 'nmap_udp.txt', 'Nmap UDP Scan', 'nmap')
    
    def gobuster_common(self) -> Dict:
        """Run Gobuster with common wordlist (HTB-optimized)"""
        gobuster_config = self.config['gobuster']
        wordlist = self.get_wordlist_path('common')  # Use HTB-optimized small wordlist
        
        command = [
            'gobuster', 'dir',
            '-u', f'http://{self.target_ip}',
            '-w', wordlist,
            '-x', gobuster_config['extensions'],
            '-t', str(gobuster_config['threads']),
            '--timeout', gobuster_config['timeout'],
            '--no-error'
        ]
        
        if gobuster_config['include_length']:
            command.append('-l')
        
        if gobuster_config['status_codes']:
            command.extend(['-s', gobuster_config['status_codes']])
        
        return self.run_command(command, 'gobuster_common.txt', 'Gobuster Common Wordlist', 'gobuster')
    
    def gobuster_big(self) -> Dict:
        """Run Gobuster with big wordlist"""
        gobuster_config = self.config['gobuster']
        wordlist = self.get_wordlist_path('big')
        
        command = [
            'gobuster', 'dir',
            '-u', f'http://{self.target_ip}',
            '-w', wordlist,
            '-x', gobuster_config['extensions'],
            '-t', str(gobuster_config['threads']),
            '--timeout', gobuster_config['timeout'],
            '--no-error'
        ]
        
        if gobuster_config['include_length']:
            command.append('-l')
        
        if gobuster_config['status_codes']:
            command.extend(['-s', gobuster_config['status_codes']])
        
        return self.run_command(command, 'gobuster_big.txt', 'Gobuster Big Wordlist', 'gobuster')
    
    def feroxbuster_scan(self) -> Dict:
        """Run Feroxbuster directory enumeration"""
        ferox_config = self.config['feroxbuster']
        wordlist = self.get_wordlist_path(ferox_config['wordlist_size'])
        
        command = [
            'feroxbuster',
            '-u', f'http://{self.target_ip}',
            '-w', wordlist,
            '-x', ferox_config['extensions'],
            '-t', str(ferox_config['threads']),
            '--timeout', str(ferox_config['timeout']),
            '-d', str(ferox_config['depth']),
            '--no-recursion',
            '-q'  # Quiet mode for cleaner output
        ]
        
        return self.run_command(command, 'feroxbuster.txt', 'Feroxbuster Directory Enumeration', 'feroxbuster')
    
    def ffuf_scan(self) -> Dict:
        """Run ffuf web fuzzer"""
        ffuf_config = self.config['ffuf']
        wordlist = self.get_wordlist_path('common')
        
        command = [
            'ffuf',
            '-u', f'http://{self.target_ip}/FUZZ',
            '-w', wordlist,
            '-e', ffuf_config['extensions'],
            '-t', str(ffuf_config['threads']),
            '-timeout', str(ffuf_config['timeout']),
            '-mc', ffuf_config['match_codes'],
            '-c'  # Colorize output
        ]
        
        # Add filter by size if configured
        if ffuf_config['filter_size']:
            command.extend(['-fs', ffuf_config['filter_size']])
        
        return self.run_command(command, 'ffuf.txt', 'ffuf Web Fuzzer', 'ffuf')
    
    def nikto_scan(self) -> Dict:
        """Run Nikto web scanner using configuration"""
        nikto_config = self.config['nikto']
        command = [
            'nikto',
            '-h', self.target_ip,
            '-Format', nikto_config['format'],
            '-maxtime', str(nikto_config['max_scan_time'])
        ]
        return self.run_command(command, 'nikto.txt', 'Nikto Web Scanner', 'nikto')
    
    def whatweb_scan(self) -> Dict:
        """Run WhatWeb technology detection using configuration"""
        whatweb_config = self.config['whatweb']
        command = [
            'whatweb',
            '-v' if whatweb_config['verbosity'] == 'verbose' else '',
            f'-a{whatweb_config["aggression"]}',
            self.target_ip
        ]
        # Remove empty strings from command
        command = [arg for arg in command if arg]
        return self.run_command(command, 'whatweb.txt', 'WhatWeb Technology Detection', 'whatweb')
    
    def theharvester_scan(self) -> Dict:
        """Run theHarvester for email and subdomain gathering"""
        harvester_config = self.config['theharvester']
        
        # Extract domain from IP (for HTB, we'll use the IP directly)
        # In real scenarios, you might want to use a domain name
        domain = self.target_ip
        
        command = [
            'theHarvester',
            '-d', domain,
            '-b', harvester_config['data_source'],
            '-l', str(harvester_config['limit'])
        ]
        
        return self.run_command(command, 'theharvester.txt', 'theHarvester Email/Subdomain Gathering', 'theharvester')
    
    def dnsrecon_scan(self) -> Dict:
        """Run DNSrecon for DNS enumeration"""
        dnsrecon_config = self.config['dnsrecon']
        
        command = [
            'dnsrecon',
            '-d', self.target_ip,
            '-t', dnsrecon_config['record_types'],
            '--threads', str(dnsrecon_config['threads'])
        ]
        
        return self.run_command(command, 'dnsrecon.txt', 'DNSrecon DNS Enumeration', 'dnsrecon')
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report with enhanced formatting"""
        summary_file = Path(self.output_dir) / 'SUMMARY_REPORT.md'
        
        # Calculate total execution time and file sizes
        total_time = sum(result.get('execution_time', 0) for result in self.results.values())
        total_size = sum(result.get('file_size', 0) for result in self.results.values())
        successful_scans = sum(1 for result in self.results.values() if result['status'] == 'success')
        
        with open(summary_file, 'w') as f:
            f.write("# ⚡ BoxRecon Reconnaissance Report\n\n")
            
            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            f.write(f"**Target IP:** `{self.target_ip}`\n")
            f.write(f"**Scan Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Output Directory:** `{self.output_dir}`\n")
            f.write(f"**Total Scans:** {len(self.results)} ({successful_scans} successful)\n")
            f.write(f"**Total Execution Time:** {total_time:.1f} seconds ({total_time/60:.1f} minutes)\n")
            f.write(f"**Total Output Size:** {total_size:,} bytes ({total_size/1024:.1f} KB)\n")
            f.write(f"**Configuration Timeout:** {self.config['general']['scan_timeout']} seconds\n\n")
            
            # Scan Results
            f.write("## 🔍 Executed Scans\n\n")
            for scan_name, result in self.results.items():
                status_emoji = {
                    'success': '✅',
                    'failed': '❌', 
                    'timeout': '⏰',
                    'not_found': '🚫',
                    'error': '💥'
                }.get(result['status'], '❓')
                
                f.write(f"### {status_emoji} {scan_name.replace('_', ' ').title()}\n\n")
                f.write(f"- **Status:** {result['status'].upper()}\n")
                f.write(f"- **Output File:** [`{Path(result['output_file']).name}`]({result['output_file']})\n")
                
                if 'execution_time' in result:
                    f.write(f"- **Execution Time:** {result['execution_time']:.2f} seconds\n")
                
                if 'file_size' in result:
                    f.write(f"- **File Size:** {result['file_size']:,} bytes\n")
                
                if 'return_code' in result:
                    f.write(f"- **Return Code:** {result['return_code']}\n")
                
                if result['status'] == 'timeout':
                    f.write(f"- **Timeout Duration:** {result.get('timeout_duration', 'Unknown')} seconds\n")
                    f.write("- **Recommendation:** Consider increasing timeout or using smaller wordlists\n")
                
                if result['status'] == 'failed':
                    f.write("- **Recommendation:** Check tool installation and target accessibility\n")
                
                f.write("\n")
            
            # Configuration Summary
            f.write("## ⚙️ Configuration Used\n\n")
            f.write(f"- **Scan Timeout:** {self.config['general']['scan_timeout']} seconds\n")
            f.write(f"- **Nmap Timing:** {self.config['nmap']['timing']}\n")
            f.write(f"- **Gobuster Threads:** {self.config['gobuster']['threads']}\n")
            f.write(f"- **Output Formatting:** {'Enabled' if self.config['output']['highlight_important'] else 'Disabled'}\n\n")
            
            # Quick Analysis Tips
            f.write("## 💡 Quick Analysis Tips\n\n")
            f.write("### 🔓 Port Scanning (Nmap)\n")
            f.write("- Look for lines with `🔓` indicating open ports\n")
            f.write("- Focus on unusual or high-numbered ports\n")
            f.write("- Check service versions for known vulnerabilities\n\n")
            
            f.write("### 📁 Directory Enumeration (Gobuster/Feroxbuster/ffuf)\n")
            f.write("- `📁` indicates accessible directories (200 status)\n")
            f.write("- `↪️` shows redirects (30x status) - often interesting\n")
            f.write("- `🔒` shows forbidden access (40x status) - may be worth investigating\n\n")
            
            f.write("### ⚠️ Web Vulnerabilities (Nikto)\n")
            f.write("- `⚠️` highlights potential vulnerabilities\n")
            f.write("- `ℹ️` shows informational findings\n")
            f.write("- Look for CVE references and version disclosures\n\n")
            
            f.write("### 🔧 Technology Stack (WhatWeb)\n")
            f.write("- `🔧` indicates detected technologies\n")
            f.write("- Note web servers, frameworks, and CMS versions\n")
            f.write("- Research known vulnerabilities for identified technologies\n\n")
            
            f.write("### 📧 Information Gathering (theHarvester)\n")
            f.write("- `📧` highlights discovered email addresses\n")
            f.write("- `🌐` shows subdomains and hosts\n")
            f.write("- Useful for social engineering and further enumeration\n\n")
            
            f.write("### 🔍 DNS Enumeration (DNSrecon)\n")
            f.write("- `🔍` indicates DNS records found\n")
            f.write("- Look for A, AAAA, CNAME, MX, NS, TXT records\n")
            f.write("- May reveal additional hosts and services\n\n")
            
            # HTB-Specific Tips
            f.write("## 🎯 HTB-Specific Recommendations\n\n")
            f.write("### Initial Enumeration\n")
            f.write("1. **Start with Nmap Quick Scan** - identifies open services quickly\n")
            f.write("2. **Check common web directories** - many HTB machines have web components\n")
            f.write("3. **Look for version information** - often key to finding exploits\n\n")
            
            f.write("### Common HTB Patterns\n")
            f.write("- **SSH (22):** Look for weak credentials or key-based auth\n")
            f.write("- **HTTP/HTTPS (80/443):** Always enumerate directories and check source\n")
            f.write("- **FTP (21):** Check for anonymous access\n")
            f.write("- **SMB (139/445):** Enumerate shares and check for null sessions\n")
            f.write("- **DNS (53):** Often reveals additional information via zone transfers\n")
            f.write("- **SNMP (161 UDP):** Check for default community strings\n")
            f.write("- **NFS (2049):** Look for exported file systems\n\n")
            
            # Next Steps
            f.write("## 🚀 Next Steps\n\n")
            f.write("### Immediate Actions\n")
            f.write("- [ ] Review all scan outputs for open ports and services\n")
            f.write("- [ ] Investigate any discovered web directories manually\n")
            f.write("- [ ] Research CVEs for identified service versions\n")
            f.write("- [ ] Check for default credentials on discovered services\n\n")
            
            f.write("### Advanced Enumeration\n")
            f.write("- [ ] Run targeted scans on interesting ports\n")
            f.write("- [ ] Enumerate specific services (SMB, SNMP, etc.)\n")
            f.write("- [ ] Check for subdomain enumeration if web services found\n")
            f.write("- [ ] Look for hidden parameters in web applications\n\n")
            
            # Footer
            f.write("---\n")
            f.write("## ⚠️ Ethical Use Reminder\n\n")
            f.write("This report was generated using BoxRecon for authorized security testing purposes.\n")
            f.write("Ensure you have proper authorization before conducting any security assessments.\n")
            f.write("The author is not responsible for any misuse of this tool or its output.\n\n")
            f.write("---\n")
            f.write(f"*Report generated by BoxRecon v1.0.0 on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Created by [hckerhub](https://hackerhub.me) | Support: [Buy Me a Coffee ☕](https://buymeacoffee.com/hckerhub)*\n")
        
        print(f"{Colors.GREEN}📋 Enhanced summary report generated: {summary_file}{Colors.END}")
        print(f"{Colors.CYAN}💡 Tip: Open the summary report for detailed analysis guidance{Colors.END}")
    
    def run_attacks(self, selected_attacks: List[str]):
        """Execute selected attacks"""
        attack_methods = {
            'nmap_quick': self.nmap_quick_scan,
            'nmap_full': self.nmap_full_scan,
            'nmap_udp': self.nmap_udp_scan,
            'gobuster_common': self.gobuster_common,
            'gobuster_big': self.gobuster_big,
            'feroxbuster': self.feroxbuster_scan,
            'ffuf': self.ffuf_scan,
            'nikto': self.nikto_scan,
            'whatweb': self.whatweb_scan,
            'theharvester': self.theharvester_scan,
            'dnsrecon': self.dnsrecon_scan
        }
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Starting reconnaissance on {self.target_ip}...{Colors.END}\n")
        
        for attack in selected_attacks:
            if attack in attack_methods:
                self.results[attack] = attack_methods[attack]()
                print()  # Add spacing between attacks
        
        self.generate_summary_report()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All scans completed!{Colors.END}")
        print(f"{Colors.CYAN}📁 Results saved in: {self.output_dir}{Colors.END}")
        print(f"{Colors.CYAN}📋 Check SUMMARY_REPORT.md for an overview{Colors.END}")
    
    def check_dependencies(self):
        """Check if required tools are installed"""
        tools = ['nmap', 'gobuster', 'nikto', 'whatweb', 'feroxbuster', 'ffuf', 'theHarvester', 'dnsrecon']
        missing_tools = []
        
        print(f"{Colors.YELLOW}🔍 Checking dependencies...{Colors.END}")
        
        for tool in tools:
            try:
                subprocess.run(['which', tool], capture_output=True, check=True)
                print(f"{Colors.GREEN}✅ {tool} found{Colors.END}")
            except subprocess.CalledProcessError:
                print(f"{Colors.YELLOW}⚠️  {tool} not found{Colors.END}")
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"\n{Colors.YELLOW}⚠️  Missing tools: {', '.join(missing_tools)}{Colors.END}")
            print(f"{Colors.CYAN}💡 Install missing tools to use all features{Colors.END}")
            return False
        else:
            print(f"{Colors.GREEN}✅ All dependencies found!{Colors.END}")
            return True
    
    def run(self):
        """Main execution method"""
        # Show ethical disclaimer first (unless skipped)
        if not self.skip_disclaimer:
            self.show_disclaimer()
        else:
            print(f"{Colors.YELLOW}⚠️  Disclaimer skipped - Remember to use this tool ethically and legally!{Colors.END}\n")
        
        # Show banner after disclaimer acceptance
        self.print_banner()
        
        # Check dependencies
        self.check_dependencies()
        print()
        
        # Get target IP
        self.target_ip = self.get_target_ip()
        
        # Create output directory
        self.output_dir = self.create_output_directory(self.target_ip)
        
        # Get attack selection
        selected_attacks = self.show_attack_menu()
        
        # Confirm before starting
        print(f"\n{Colors.BOLD}📋 Selected attacks:{Colors.END}")
        for attack in selected_attacks:
            print(f"  • {attack.replace('_', ' ').title()}")
        
        confirm = input(f"\n{Colors.CYAN}🚀 Start reconnaissance? (y/N): {Colors.END}").strip().lower()
        if confirm in ['y', 'yes']:
            self.run_attacks(selected_attacks)
        else:
            print(f"{Colors.YELLOW}👋 Reconnaissance cancelled.{Colors.END}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="BoxRecon - Advanced Machine Reconnaissance Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 boxrecon.py                  # Interactive mode
  python3 boxrecon.py --help          # Show this help
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='BoxRecon 1.0.0'
    )
    
    parser.add_argument(
        '--skip-disclaimer',
        action='store_true',
        help='Skip the ethical use disclaimer (for automated use - you still must use ethically!)'
    )
    
    args = parser.parse_args()
    
    try:
        boxrecon = BoxRecon(skip_disclaimer=args.skip_disclaimer)
        boxrecon.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 BoxRecon interrupted by user. Goodbye!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {str(e)}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main() 