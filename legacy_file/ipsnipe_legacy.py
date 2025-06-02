#!/usr/bin/env python3
"""
ipsnipe - A user-friendly CLI tool for machine reconnaissance
Author: hckerhub (X: @hckerhub)
Website: https://hackerhub.me
GitHub: https://github.com/hckerhub
Version: 2.1
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

class ipsnipe:
    def __init__(self, skip_disclaimer=False, sudo_mode=None):
        self.target_ip = None
        self.output_dir = None
        self.results = {}
        self.config = self.load_config()
        self.skip_disclaimer = skip_disclaimer
        self.sudo_mode = sudo_mode  # None = ask user, True = enabled, False = disabled
        self.open_ports = []  # Store discovered open ports
        self.web_ports = []   # Store discovered web service ports
        self.responsive_web_ports = []  # Store web ports that actually respond with content
    
    def load_config(self) -> Dict:
        """Load configuration from config.toml file (shared with main system)"""
        config_file = Path("config.toml")
        
        # Import the main configuration system for consistency
        try:
            # Try to use the main config system if available
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from ipsnipe.core.config import ConfigManager
            
            config = ConfigManager.load_config()
            print(f"{Colors.GREEN}✅ Legacy system using shared configuration system{Colors.END}")
            return config
            
        except ImportError:
            # Fallback to basic config loading if main system not available
            if config_file.exists():
                try:
                    user_config = load_toml(config_file)
                    print(f"{Colors.GREEN}✅ Legacy system loaded configuration from config.toml{Colors.END}")
                    return user_config
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠️  Error loading config.toml: {e}{Colors.END}")
            
            # Absolute minimal fallback
            print(f"{Colors.YELLOW}⚠️  Using minimal fallback configuration{Colors.END}")
            return {
                'general': {'scan_timeout': 700, 'default_threads': 50},
                'nmap': {'quick_ports': '1000', 'timing': 'T4'},
                'gobuster': {'threads': 50, 'extensions': 'php,html,txt'},
                'nikto': {'timeout': 700},
                'wordlists': {'base_dir': '/usr/share/wordlists'}
            }
    
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
        
        print(f"{Colors.YELLOW}ipsnipe is designed for AUTHORIZED security testing and educational purposes only.{Colors.END}\n")
        
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
        """Display the ipsnipe banner"""
        print(BANNER)
        print(f"{Colors.YELLOW}Welcome to ipsnipe - Your Advanced Reconnaissance Framework!{Colors.END}")
        print(f"{Colors.BLUE}Created by hckerhub | {Colors.CYAN}https://hackerhub.me{Colors.END}")
        print(f"{Colors.PURPLE}Support the project: {Colors.YELLOW}https://buymeacoffee.com/hckerhub{Colors.END}\n")
    
    def check_root_privileges(self) -> bool:
        """Check if running with root privileges"""
        import os
        return os.geteuid() == 0
    
    def test_sudo_access(self) -> bool:
        """Test if sudo access is available"""
        try:
            result = subprocess.run(['sudo', '-n', 'true'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_sudo_mode_preference(self) -> bool:
        """Get user preference for sudo mode with intelligent recommendations"""
        if self.sudo_mode is not None:
            return self.sudo_mode
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔐 Enhanced Scanning Mode Configuration:{Colors.END}")
        
        is_root = self.check_root_privileges()
        has_sudo = self.test_sudo_access()
        
        if is_root:
            print(f"{Colors.GREEN}✅ Running as root - Full scanning capabilities available{Colors.END}")
            return True
        elif has_sudo:
            print(f"{Colors.YELLOW}🔑 Sudo access detected - Enhanced scans available{Colors.END}")
        else:
            print(f"{Colors.RED}⚠️  No root/sudo access - Limited to unprivileged scans{Colors.END}")
        
        print(f"\n{Colors.CYAN}Enhanced Mode Benefits:{Colors.END}")
        print(f"  ✅ SYN Scans (faster, more stealthy)")
        print(f"  ✅ OS Detection (identify target operating system)")
        print(f"  ✅ UDP Scans (discover UDP services like DNS, SNMP)")
        print(f"  ✅ Advanced Nmap scripts")
        
        print(f"\n{Colors.YELLOW}Standard Mode Features:{Colors.END}")
        print(f"  ✅ TCP Connect Scans (reliable, works without root)")
        print(f"  ✅ Service Version Detection")
        print(f"  ✅ All web enumeration tools")
        print(f"  ✅ DNS and subdomain enumeration")
        
        if not has_sudo and not is_root:
            print(f"\n{Colors.RED}💡 Running in Standard Mode (no sudo access detected){Colors.END}")
            return False
        
        while True:
            if has_sudo or is_root:
                prompt = f"\n{Colors.CYAN}Enable Enhanced Mode with sudo privileges? (y/N): {Colors.END}"
                response = input(prompt).strip().lower()
                
                if response in ['y', 'yes']:
                    print(f"{Colors.GREEN}🚀 Enhanced Mode enabled - Using advanced scanning techniques{Colors.END}")
                    return True
                elif response in ['n', 'no', '']:
                    print(f"{Colors.YELLOW}📊 Standard Mode enabled - Using unprivileged scans{Colors.END}")
                    return False
                else:
                    print(f"{Colors.RED}Please enter 'yes' or 'no'{Colors.END}")
            else:
                return False
    
    def validate_ip(self, ip_string: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
    
    def validate_port_range(self, port_range: str) -> bool:
        """Validate port range format (e.g., '80', '1-1000', '80,443,8080')"""
        if not port_range.strip():
            return False
        
        # Handle 'default' keyword
        if port_range.strip().lower() == 'default':
            return True
        
        try:
            # Handle comma-separated ports
            if ',' in port_range:
                ports = port_range.split(',')
                for port in ports:
                    port_num = int(port.strip())
                    if not (1 <= port_num <= 65535):
                        return False
                return True
            
            # Handle range (e.g., '1-1000')
            elif '-' in port_range:
                start, end = port_range.split('-', 1)
                start_port = int(start.strip())
                end_port = int(end.strip())
                if not (1 <= start_port <= end_port <= 65535):
                    return False
                return True
            
            # Handle single port
            else:
                port_num = int(port_range.strip())
                return 1 <= port_num <= 65535
                
        except ValueError:
            return False
    
    def get_port_range_input(self) -> str:
        """Get port range from user with validation"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔌 Port Range Configuration:{Colors.END}")
        print(f"{Colors.YELLOW}Examples:{Colors.END}")
        print(f"  • {Colors.CYAN}80{Colors.END} - Single port")
        print(f"  • {Colors.CYAN}1-1000{Colors.END} - Port range")
        print(f"  • {Colors.CYAN}80,443,8080{Colors.END} - Specific ports")
        print(f"  • {Colors.CYAN}1-65535{Colors.END} - All ports")
        print(f"  • {Colors.GREEN}default{Colors.END} - Use default configuration")
        
        while True:
            port_input = input(f"\n{Colors.CYAN}🎯 Enter port range (or 'default'): {Colors.END}").strip()
            
            if port_input.lower() == 'default':
                return 'default'
            elif self.validate_port_range(port_input):
                print(f"{Colors.GREEN}✅ Valid port range: {port_input}{Colors.END}")
                return port_input
            else:
                print(f"{Colors.RED}❌ Invalid port range. Please try again.{Colors.END}")
    
    def test_web_port_responsiveness(self, port: int) -> dict:
        """Test if a web port responds with actual content"""
        protocols = ['https' if port in [443, 8443] else 'http']
        if port == 443:
            protocols = ['https', 'http']  # Try both for 443
        
        for protocol in protocols:
            try:
                import urllib.request
                import urllib.error
                import ssl
                
                url = f"{protocol}://{self.target_ip}:{port}/"
                
                # Create SSL context that doesn't verify certificates
                if protocol == 'https':
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                    opener = urllib.request.build_opener(https_handler)
                    urllib.request.install_opener(opener)
                
                request = urllib.request.Request(url)
                request.add_header('User-Agent', 'ipsnipe/2.1')
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    status_code = response.getcode()
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', '0')
                    server = response.headers.get('server', '')
                    
                    # Try to read a bit of content
                    try:
                        content_sample = response.read(1024).decode('utf-8', errors='ignore')
                        has_content = len(content_sample.strip()) > 0
                    except:
                        has_content = False
                    
                    return {
                        'responsive': True,
                        'protocol': protocol,
                        'status_code': status_code,
                        'content_type': content_type,
                        'content_length': content_length,
                        'server': server,
                        'has_content': has_content,
                        'interesting': status_code in [200, 301, 302] and (has_content or status_code != 404)
                    }
                    
            except Exception as e:
                last_error = str(e)
                continue
        
        return {'responsive': False, 'protocol': 'http', 'error': last_error if 'last_error' in locals() else 'Connection failed'}
    
    def parse_nmap_output_for_ports(self, output_file: str) -> None:
        """Parse nmap output to extract open ports and identify web services"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Reset port lists
            self.open_ports = []
            self.web_ports = []
            self.responsive_web_ports = []
            
            # Common web service patterns
            web_services = ['http', 'https', 'http-proxy', 'http-alt', 'ssl/http', 'ssl/https', 'www', 'web']
            
            # Parse nmap output for open ports - more flexible regex patterns
            # Pattern 1: Standard format - match until end of line only
            port_lines = re.findall(r'(\d+)/tcp\s+open\s+([^\n]+)', content)
            
            # Clean up service names (take only first few words)
            cleaned_port_lines = []
            for port, service in port_lines:
                # Split service string and take only first 2-3 words
                service_words = service.strip().split()
                if service_words:
                    service_clean = ' '.join(service_words[:3])  # Take max 3 words
                else:
                    service_clean = 'unknown'
                cleaned_port_lines.append((port, service_clean))
            port_lines = cleaned_port_lines
            
            # Pattern 2: Just port/tcp open (without service name)
            if not port_lines:
                port_lines = re.findall(r'(\d+)/tcp\s+open', content)
                port_lines = [(port, 'unknown') for port in port_lines]
            
            # Debug output
            if port_lines:
                print(f"{Colors.BLUE}📝 Debug - Found ports in nmap output: {port_lines}{Colors.END}")
            
            for port_num, service in port_lines:
                port = int(port_num)
                self.open_ports.append(port)
                
                # Debug output for service detection
                print(f"{Colors.BLUE}📌 Checking port {port} with service: '{service}'{Colors.END}")
                
                # Check if it's a web service - be more inclusive
                # Standard web ports
                standard_web_ports = [80, 443, 8080, 8443, 8000, 8888, 9000, 3000, 5000, 8081, 8082, 8090]
                
                # Check if it's a web service
                is_web_service = False
                
                # Check by port number first (most reliable)
                if port in standard_web_ports:
                    is_web_service = True
                    if port == 80 or port == 8080:
                        print(f"{Colors.GREEN}🌐 Port {port} detected as HTTP (standard web port){Colors.END}")
                    elif port == 443 or port == 8443:
                        print(f"{Colors.GREEN}🌐 Port {port} detected as HTTPS (standard SSL port){Colors.END}")
                
                # Check by service name
                elif service and service.lower() != 'unknown':
                    service_lower = service.lower()
                    # Exclude SSH and other non-web services
                    non_web_services = ['ssh', 'telnet', 'ftp', 'smtp', 'pop3', 'imap', 'rdp', 'vnc', 'mysql', 'postgresql', 'mssql', 'oracle', 'smb', 'netbios']
                    
                    # Check if it's definitely not a web service
                    if any(nws in service_lower for nws in non_web_services):
                        is_web_service = False
                        print(f"{Colors.YELLOW}➖ Port {port} excluded - Non-web service detected: {service}{Colors.END}")
                    # Check if any web service pattern matches
                    elif any(ws in service_lower for ws in web_services):
                        is_web_service = True
                        print(f"{Colors.GREEN}🌐 Port {port} detected as web service (service: {service}){Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}❓ Port {port} - Unknown service type: {service}{Colors.END}")
                
                if is_web_service:
                    self.web_ports.append(port)
            
            if self.open_ports:
                print(f"{Colors.GREEN}🔓 Discovered {len(self.open_ports)} open ports: {sorted(self.open_ports)}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Warning: No open ports detected in nmap output. Parsing may have failed.{Colors.END}")
                # Try alternative parsing as last resort
                alt_ports = re.findall(r'(\d+)/tcp', content)
                if alt_ports:
                    print(f"{Colors.YELLOW}📝 Found ports using alternative parsing: {alt_ports}{Colors.END}")
                    for port_str in alt_ports:
                        port = int(port_str)
                        self.open_ports.append(port)
                        if port in [80, 443, 8080, 8443, 8000, 8888, 9000, 3000, 5000]:
                            self.web_ports.append(port)
                            print(f"{Colors.GREEN}🌐 Port {port} added as web service (fallback detection){Colors.END}")
            
            if self.web_ports:
                print(f"{Colors.CYAN}🌐 Detected {len(self.web_ports)} web services on ports: {sorted(self.web_ports)}{Colors.END}")
                
                # Test web port responsiveness
                print(f"{Colors.YELLOW}🔍 Testing web port responsiveness...{Colors.END}")
                for port in self.web_ports:
                    response_info = self.test_web_port_responsiveness(port)
                    if response_info['responsive']:
                        self.responsive_web_ports.append({
                            'port': port,
                            'info': response_info
                        })
                        status_icon = "🟢" if response_info['interesting'] else "🟡"
                        print(f"  {status_icon} Port {port} ({response_info['protocol']}) - Status: {response_info.get('status_code', 'N/A')}")
                    else:
                        print(f"  🔴 Port {port} - Not responsive")
                
                # Sort responsive ports by interestingness
                self.responsive_web_ports.sort(key=lambda x: (
                    x['info']['interesting'],  # Interesting ports first
                    x['info']['status_code'] == 200,  # 200 OK responses first
                    x['info']['has_content']  # Ports with content first
                ), reverse=True)
                
                if self.responsive_web_ports:
                    interesting_ports = [p['port'] for p in self.responsive_web_ports if p['info']['interesting']]
                    if interesting_ports:
                        print(f"{Colors.GREEN}🎯 Prioritizing interesting web ports: {interesting_ports}{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}📝 All web ports will be tested{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}⚠️  No responsive web services - HTTP scans may have limited results{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  No web services detected - HTTP scans will be skipped{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse nmap output for port detection: {e}{Colors.END}")
    
    def should_run_web_scan(self, scan_type: str) -> bool:
        """Determine if web-based scans should run based on discovered ports"""
        web_scan_types = ['gobuster_common', 'gobuster_big', 'feroxbuster', 'ffuf', 'nikto', 'whatweb']
        
        if scan_type not in web_scan_types:
            return True  # Always run non-web scans
        
        if not self.web_ports:
            print(f"{Colors.YELLOW}⚠️  No web services automatically detected for {scan_type.replace('_', ' ').title()}{Colors.END}")
            
            # Check if common web ports are in the open ports list as a fallback
            common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 9000, 3000, 5000]
            found_web_ports = [port for port in self.open_ports if port in common_web_ports]
            
            if found_web_ports:
                print(f"{Colors.YELLOW}🔧 Found potential web ports in open ports list: {found_web_ports}{Colors.END}")
                self.web_ports.extend(found_web_ports)
                self.web_ports = list(set(self.web_ports))  # Remove duplicates
                print(f"{Colors.GREEN}✅ Added {found_web_ports} to web ports list - proceeding with scan{Colors.END}")
                return True
            
            # Last resort - ask user
            print(f"{Colors.YELLOW}Would you like to force web scans anyway? Common for HTB boxes.{Colors.END}")
            force = input(f"{Colors.CYAN}Force web scan on port 80? (y/N): {Colors.END}").strip().lower()
            if force in ['y', 'yes']:
                self.web_ports.append(80)
                print(f"{Colors.GREEN}✅ Forcing web scan on port 80{Colors.END}")
                return True
            
            print(f"{Colors.YELLOW}⏭️  Skipping {scan_type.replace('_', ' ').title()} - No web services found{Colors.END}")
            return False
        
        # If we have responsive ports, prioritize those; otherwise use all detected web ports
        if self.responsive_web_ports:
            return True
        elif self.web_ports:
            print(f"{Colors.YELLOW}⚠️  {scan_type.replace('_', ' ').title()} - No responsive web ports, but trying detected web services{Colors.END}")
            return True
        
        return False
    
    def get_best_web_port(self) -> tuple:
        """Get the most promising web port and protocol for scanning"""
        # Prioritize responsive and interesting ports
        if self.responsive_web_ports:
            best_port_info = self.responsive_web_ports[0]  # Already sorted by interestingness
            port = best_port_info['port']
            protocol = best_port_info['info']['protocol']
            return port, protocol
        
        # Fallback to first discovered web port
        if self.web_ports:
            # Sort web ports to prioritize standard ports
            sorted_ports = sorted(self.web_ports, key=lambda p: (
                p not in [80, 443, 8080, 8443],  # Standard ports first
                p  # Then by port number
            ))
            port = sorted_ports[0]
            protocol = 'https' if port in [443, 8443] else 'http'
            return port, protocol
        
        # Last resort - use port 80
        print(f"{Colors.YELLOW}⚠️  No web ports detected, defaulting to port 80{Colors.END}")
        return 80, 'http'
    
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
        dir_name = f"ipsnipe_{ip}_{timestamp}"
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
                f.write(f"ipsnipe Scan Report - {description}\n")
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
                f.write(f"ipsnipe Scan Report - {description} (TIMEOUT)\n")
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
    
    def nmap_quick_scan(self, port_range=None) -> Dict:
        """Run quick Nmap scan using configuration or custom port range"""
        nmap_config = self.config['nmap']
        
        # Determine scan type based on sudo mode
        if hasattr(self, 'enhanced_mode') and self.enhanced_mode:
            command = ['sudo', 'nmap', '-sS']  # SYN scan with sudo
            scan_description = 'Nmap Quick Scan (Enhanced SYN)'
        else:
            command = ['nmap', '-sT']  # TCP connect scan
            scan_description = 'Nmap Quick Scan (Standard TCP)'
        
        if nmap_config['enable_version_detection']:
            command.extend(['-sV', '--version-intensity', str(nmap_config['version_intensity'])])
        
        # Only enable OS detection in enhanced mode
        if nmap_config['enable_os_detection'] and hasattr(self, 'enhanced_mode') and self.enhanced_mode:
            command.append('-O')
        
        # Use custom port range if provided, otherwise use default
        if port_range and port_range != 'default':
            if ',' in port_range or '-' in port_range:
                command.extend(['-p', port_range])
            else:
                command.extend(['-p', port_range])
        else:
            command.extend(['--top-ports', str(nmap_config['quick_ports'])])
        
        command.extend([f'-{nmap_config["timing"]}', self.target_ip])
        
        result = self.run_command(command, 'nmap_quick.txt', scan_description, 'nmap')
        
        # Parse output for port detection if scan was successful
        if result['status'] == 'success':
            self.parse_nmap_output_for_ports(result['output_file'])
        
        return result
    
    def nmap_full_scan(self, port_range=None) -> Dict:
        """Run full Nmap scan using configuration or custom port range"""
        nmap_config = self.config['nmap']
        command = ['nmap', '-sT']
        
        if nmap_config['enable_version_detection']:
            command.extend(['-sV', '--version-intensity', '9'])
        
        if nmap_config['enable_os_detection']:
            command.append('-O')
        
        # Use custom port range if provided, otherwise scan all ports
        if port_range and port_range != 'default':
            command.extend(['-p', port_range])
        else:
            command.extend(['-p-'])
        
        command.append(f'-{nmap_config["timing"]}')
        
        if nmap_config['enable_script_scan']:
            command.extend(['--script=default,vuln'])
        
        command.append(self.target_ip)
        
        result = self.run_command(command, 'nmap_full.txt', 'Nmap Full Scan', 'nmap')
        
        # Parse output for port detection if scan was successful
        if result['status'] == 'success':
            self.parse_nmap_output_for_ports(result['output_file'])
        
        return result
    
    def nmap_udp_scan(self, port_range=None) -> Dict:
        """Run UDP Nmap scan using configuration or custom port range"""
        # UDP scans require root privileges
        if not (hasattr(self, 'enhanced_mode') and self.enhanced_mode):
            print(f"{Colors.YELLOW}⏭️  Skipping UDP Scan - Requires Enhanced Mode (sudo privileges){Colors.END}")
            return {
                'status': 'skipped',
                'reason': 'UDP scans require root privileges (Enhanced Mode)',
                'recommendation': 'Enable Enhanced Mode to use UDP scanning'
            }
        
        nmap_config = self.config['nmap']
        command = ['sudo', 'nmap', '-sU']
        
        # Use custom port range if provided, otherwise use default UDP ports
        if port_range and port_range != 'default':
            command.extend(['-p', port_range])
        else:
            command.extend(['--top-ports', str(nmap_config['udp_ports'])])
        
        command.extend([f'-{nmap_config["timing"]}', self.target_ip])
        
        result = self.run_command(command, 'nmap_udp.txt', 'Nmap UDP Scan (Enhanced)', 'nmap')
        
        # Parse output for port detection if scan was successful
        if result['status'] == 'success':
            self.parse_nmap_output_for_ports(result['output_file'])
        
        return result
    
    def gobuster_common(self) -> Dict:
        """Run Gobuster with common wordlist (HTB-optimized)"""
        if not self.should_run_web_scan('gobuster_common'):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        gobuster_config = self.config['gobuster']
        wordlist = self.get_wordlist_path('common')
        
        # Use the best available web port
        target_port, protocol = self.get_best_web_port()
        
        command = [
            'gobuster', 'dir',
            '-u', f'{protocol}://{self.target_ip}:{target_port}',
            '-w', wordlist,
            '-x', gobuster_config['extensions'],
            '-t', str(gobuster_config['threads']),
            '--timeout', gobuster_config['timeout'],
            '--no-error'
        ]
        
        # Add SSL options if using HTTPS
        if protocol == 'https' or target_port in [443, 8443]:
            command.append('-k')  # Skip SSL certificate verification
        
        # Length is shown by default in gobuster dir mode
        # Removed the incorrect -l flag that was causing errors
        
        if gobuster_config['status_codes']:
            command.extend(['-s', gobuster_config['status_codes'], '-b', ''])  # Clear default blacklist
        
        # Add quiet mode
        command.append('-q')
        
        description = f'Gobuster Common Wordlist ({protocol.upper()} Port {target_port})'
        if self.responsive_web_ports and target_port == self.responsive_web_ports[0]['port']:
            description += ' [Priority Target]'
        
        return self.run_command(command, 'gobuster_common.txt', description, 'gobuster')
    
    def gobuster_big(self) -> Dict:
        """Run Gobuster with big wordlist"""
        if not self.should_run_web_scan('gobuster_big'):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        gobuster_config = self.config['gobuster']
        wordlist = self.get_wordlist_path('big')
        
        # Use the best available web port
        target_port, protocol = self.get_best_web_port()
        
        command = [
            'gobuster', 'dir',
            '-u', f'{protocol}://{self.target_ip}:{target_port}',
            '-w', wordlist,
            '-x', gobuster_config['extensions'],
            '-t', str(gobuster_config['threads']),
            '--timeout', gobuster_config['timeout'],
            '--no-error'
        ]
        
        # Add SSL options if using HTTPS
        if protocol == 'https' or target_port in [443, 8443]:
            command.append('-k')  # Skip SSL certificate verification
        
        # Length is shown by default in gobuster dir mode
        # Removed the incorrect -l flag that was causing errors
        
        if gobuster_config['status_codes']:
            command.extend(['-s', gobuster_config['status_codes'], '-b', ''])  # Clear default blacklist
        
        # Add quiet mode
        command.append('-q')
        
        description = f'Gobuster Big Wordlist ({protocol.upper()} Port {target_port})'
        if self.responsive_web_ports and target_port == self.responsive_web_ports[0]['port']:
            description += ' [Priority Target]'
        
        return self.run_command(command, 'gobuster_big.txt', description, 'gobuster')
    
    def feroxbuster_scan(self) -> Dict:
        """Run Feroxbuster directory enumeration"""
        if not self.should_run_web_scan('feroxbuster'):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        ferox_config = self.config['feroxbuster']
        wordlist = self.get_wordlist_path(ferox_config['wordlist_size'])
        
        # Use the best available web port
        target_port, protocol = self.get_best_web_port()
        
        command = [
            'feroxbuster',
            '-u', f'{protocol}://{self.target_ip}:{target_port}',
            '-w', wordlist,
            '-x', ferox_config['extensions'],
            '-t', str(ferox_config['threads']),
            '--timeout', str(ferox_config['timeout']),
            '-d', str(ferox_config['depth']),
            '--no-recursion',
            '-q'  # Quiet mode for cleaner output
        ]
        
        # Add SSL options if using HTTPS
        if protocol == 'https' or target_port in [443, 8443]:
            command.append('-k')  # Skip SSL certificate verification
        
        description = f'Feroxbuster Directory Enumeration ({protocol.upper()} Port {target_port})'
        if self.responsive_web_ports and target_port == self.responsive_web_ports[0]['port']:
            description += ' [Priority Target]'
        
        return self.run_command(command, 'feroxbuster.txt', description, 'feroxbuster')
    
    def ffuf_scan(self) -> Dict:
        """Run ffuf web fuzzer"""
        if not self.should_run_web_scan('ffuf'):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        ffuf_config = self.config['ffuf']
        wordlist = self.get_wordlist_path('common')
        
        # Use the best available web port
        target_port, protocol = self.get_best_web_port()
        
        command = [
            'ffuf',
            '-u', f'{protocol}://{self.target_ip}:{target_port}/FUZZ',
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
        
        # Ignore SSL certificate errors if using HTTPS
        if protocol == 'https' or target_port in [443, 8443]:
            command.append('-ic')  # Ignore certificate errors
        
        description = f'ffuf Web Fuzzer ({protocol.upper()} Port {target_port})'
        if self.responsive_web_ports and target_port == self.responsive_web_ports[0]['port']:
            description += ' [Priority Target]'
        
        return self.run_command(command, 'ffuf.txt', description, 'ffuf')
    
    def nikto_scan(self) -> Dict:
        """Run Nikto web scanner using configuration"""
        if not self.should_run_web_scan('nikto'):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        nikto_config = self.config['nikto']
        
        # Use the best available web port
        target_port, protocol = self.get_best_web_port()
        
        command = [
            'nikto',
            '-h', f'{self.target_ip}:{target_port}',
            '-maxtime', str(nikto_config['max_scan_time']),
            '-nointeractive'  # Prevent any prompts
        ]
        
        # Add SSL flag if using HTTPS
        if protocol == 'https' or target_port in [443, 8443]:
            command.extend(['-ssl', '+'])
        
        description = f'Nikto Web Scanner ({protocol.upper()} Port {target_port})'
        if self.responsive_web_ports and target_port == self.responsive_web_ports[0]['port']:
            description += ' [Priority Target]'
        
        return self.run_command(command, 'nikto.txt', description, 'nikto')
    
    def whatweb_scan(self) -> Dict:
        """Run WhatWeb technology detection using configuration"""
        if not self.should_run_web_scan('whatweb'):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        whatweb_config = self.config['whatweb']
        
        # Use the best available web port
        target_port, protocol = self.get_best_web_port()
        
        command = [
            'whatweb',
            '-v' if whatweb_config['verbosity'] == 'verbose' else '',
            f'-a{whatweb_config["aggression"]}',
            f'{protocol}://{self.target_ip}:{target_port}'
        ]
        
        # Add SSL options if using HTTPS
        if protocol == 'https' or target_port in [443, 8443]:
            command.append('--no-check-certificate')  # Skip SSL certificate verification
        
        # Remove empty strings from command
        command = [arg for arg in command if arg]
        
        description = f'WhatWeb Technology Detection ({protocol.upper()} Port {target_port})'
        if self.responsive_web_ports and target_port == self.responsive_web_ports[0]['port']:
            description += ' [Priority Target]'
        
        return self.run_command(command, 'whatweb.txt', description, 'whatweb')
    
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
            f.write("# ⚡ ipsnipe Reconnaissance Report\n\n")
            
            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            f.write(f"**Target IP:** `{self.target_ip}`\n")
            f.write(f"**Scan Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Output Directory:** `{self.output_dir}`\n")
            f.write(f"**Enhanced Mode:** {'✅ Enabled (sudo privileges)' if hasattr(self, 'enhanced_mode') and self.enhanced_mode else '❌ Disabled (standard mode)'}\n")
            f.write(f"**Total Scans:** {len(self.results)} ({successful_scans} successful)\n")
            f.write(f"**Total Execution Time:** {total_time:.1f} seconds ({total_time/60:.1f} minutes)\n")
            f.write(f"**Total Output Size:** {total_size:,} bytes ({total_size/1024:.1f} KB)\n")
            f.write(f"**Configuration Timeout:** {self.config['general']['scan_timeout']} seconds\n\n")
            
            # Port discovery summary
            if self.open_ports:
                f.write(f"**Open Ports Found:** {len(self.open_ports)} ({', '.join(map(str, sorted(self.open_ports)))})\n")
            if self.web_ports:
                f.write(f"**Web Services:** {len(self.web_ports)} detected ({', '.join(map(str, sorted(self.web_ports)))})\n")
            if self.responsive_web_ports:
                responsive_ports = [str(p['port']) for p in self.responsive_web_ports]
                f.write(f"**Responsive Web Ports:** {', '.join(responsive_ports)} (tested and confirmed active)\n")
            f.write("\n")
            
            # Scan Results
            f.write("## 🔍 Executed Scans\n\n")
            for scan_name, result in self.results.items():
                status_emoji = {
                    'success': '✅',
                    'failed': '❌', 
                    'timeout': '⏰',
                    'not_found': '🚫',
                    'error': '💥',
                    'skipped': '⏭️'
                }.get(result['status'], '❓')
                
                f.write(f"### {status_emoji} {scan_name.replace('_', ' ').title()}\n\n")
                f.write(f"- **Status:** {result['status'].upper()}\n")
                
                if result['status'] == 'skipped':
                    f.write(f"- **Reason:** {result.get('reason', 'Scan was skipped')}\n")
                    f.write("- **Recommendation:** Run an nmap scan first to detect web services\n")
                else:
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
            f.write("This report was generated using ipsnipe for authorized security testing purposes.\n")
            f.write("Ensure you have proper authorization before conducting any security assessments.\n")
            f.write("The author is not responsible for any misuse of this tool or its output.\n\n")
            f.write("---\n")
            f.write(f"*Report generated by ipsnipe v1.0.5 on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Created by [hckerhub](https://hackerhub.me) | Support: [Buy Me a Coffee ☕](https://buymeacoffee.com/hckerhub)*\n")
        
        print(f"{Colors.GREEN}📋 Enhanced summary report generated: {summary_file}{Colors.END}")
        print(f"{Colors.CYAN}💡 Tip: Open the summary report for detailed analysis guidance{Colors.END}")
    
    def run_attacks(self, selected_attacks: List[str], port_range: str = None):
        """Execute selected attacks with optional port range"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Starting reconnaissance on {self.target_ip}...{Colors.END}\n")
        
        # Get port range for nmap scans if needed
        nmap_scans = ['nmap_quick', 'nmap_full', 'nmap_udp']
        has_nmap_scans = any(scan in selected_attacks for scan in nmap_scans)
        
        if has_nmap_scans and not port_range:
            port_range = self.get_port_range_input()
        
        # Execute all selected scans
        for attack in selected_attacks:
            if attack == 'nmap_quick':
                self.results[attack] = self.nmap_quick_scan(port_range)
            elif attack == 'nmap_full':
                self.results[attack] = self.nmap_full_scan(port_range)
            elif attack == 'nmap_udp':
                self.results[attack] = self.nmap_udp_scan(port_range)
            elif attack == 'gobuster_common':
                self.results[attack] = self.gobuster_common()
            elif attack == 'gobuster_big':
                self.results[attack] = self.gobuster_big()
            elif attack == 'feroxbuster':
                self.results[attack] = self.feroxbuster_scan()
            elif attack == 'ffuf':
                self.results[attack] = self.ffuf_scan()
            elif attack == 'nikto':
                self.results[attack] = self.nikto_scan()
            elif attack == 'whatweb':
                self.results[attack] = self.whatweb_scan()
            elif attack == 'theharvester':
                self.results[attack] = self.theharvester_scan()
            elif attack == 'dnsrecon':
                self.results[attack] = self.dnsrecon_scan()
            
            # Show results status
            if attack in self.results:
                status = self.results[attack]['status']
                if status == 'skipped':
                    print(f"{Colors.YELLOW}⏭️  {attack.replace('_', ' ').title()} - {self.results[attack].get('reason', 'Skipped')}{Colors.END}")
                elif status == 'success':
                    print(f"{Colors.GREEN}✅ {attack.replace('_', ' ').title()} - Completed{Colors.END}")
                elif status == 'failed':
                    print(f"{Colors.RED}❌ {attack.replace('_', ' ').title()} - Failed{Colors.END}")
                elif status == 'timeout':
                    print(f"{Colors.YELLOW}⏰ {attack.replace('_', ' ').title()} - Timed out{Colors.END}")
            
            print()  # Add spacing between attacks
        
        self.generate_summary_report()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All scans completed!{Colors.END}")
        print(f"{Colors.CYAN}📁 Results saved in: {self.output_dir}{Colors.END}")
        print(f"{Colors.CYAN}📋 Check SUMMARY_REPORT.md for an overview{Colors.END}")
        
        # Show web service detection summary
        if self.web_ports:
            print(f"{Colors.GREEN}🌐 Web services detected on ports: {sorted(self.web_ports)}{Colors.END}")
        elif any(scan in selected_attacks for scan in ['gobuster_common', 'gobuster_big', 'feroxbuster', 'ffuf', 'nikto', 'whatweb']):
            print(f"{Colors.YELLOW}⚠️  No web services detected - some HTTP scans were skipped{Colors.END}")
        
        print(f"{Colors.CYAN}💡 Tip: Review individual scan files for detailed results{Colors.END}")
    
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
        
        # Get sudo mode preference
        self.enhanced_mode = self.get_sudo_mode_preference()
        
        # Get target IP
        self.target_ip = self.get_target_ip()
        
        # Create output directory
        self.output_dir = self.create_output_directory(self.target_ip)
        
        # Get attack selection
        selected_attacks = self.show_attack_menu()
        
        # Confirm before starting
        print(f"\n{Colors.BOLD}📋 Scan Configuration:{Colors.END}")
        print(f"  🎯 Target IP: {self.target_ip}")
        print(f"  📁 Output Directory: {self.output_dir}")
        print(f"  🔐 Enhanced Mode: {'✅ Enabled (sudo)' if self.enhanced_mode else '❌ Disabled (standard)'}")
        print(f"\n{Colors.BOLD}📋 Selected attacks:{Colors.END}")
        for attack in selected_attacks:
            enhanced_note = ""
            if attack in ['nmap_quick', 'nmap_full'] and self.enhanced_mode:
                enhanced_note = " (SYN scan + OS detection)"
            elif attack == 'nmap_udp' and not self.enhanced_mode:
                enhanced_note = " (will be skipped - requires sudo)"
            elif attack == 'nmap_udp' and self.enhanced_mode:
                enhanced_note = " (UDP scan enabled)"
            print(f"  • {attack.replace('_', ' ').title()}{enhanced_note}")
        
        confirm = input(f"\n{Colors.CYAN}🚀 Start reconnaissance? (y/N): {Colors.END}").strip().lower()
        if confirm in ['y', 'yes']:
            self.run_attacks(selected_attacks)
        else:
            print(f"{Colors.YELLOW}👋 Reconnaissance cancelled.{Colors.END}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ipsnipe - Advanced Machine Reconnaissance Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ipsnipe.py                      # Interactive mode
  python3 ipsnipe.py --enhanced           # Force enhanced mode (sudo)
  python3 ipsnipe.py --standard           # Force standard mode (no sudo)
  python3 ipsnipe.py --skip-disclaimer    # Skip disclaimer for automation

For more information, visit: https://github.com/hckerhub
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='ipsnipe 2.1'
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
    
    try:
        ipsnipe_tool = ipsnipe(skip_disclaimer=args.skip_disclaimer, sudo_mode=sudo_mode)
        ipsnipe_tool.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 ipsnipe interrupted by user. Goodbye!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {str(e)}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main() 