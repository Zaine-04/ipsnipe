#!/usr/bin/env python3
"""
Web scanner implementations for ipsnipe
Handles gobuster, feroxbuster, ffuf, nikto, and whatweb scanning
"""

import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from ..ui.colors import Colors


class WebScanners:
    """Web scanning functionality"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.responsive_web_ports = []
    
    def should_run_web_scan(self, scan_type: str, web_ports: List[int]) -> bool:
        """Determine if web scan should run based on available web ports"""
        if not web_ports:
            print(f"{Colors.YELLOW}⏭️  Skipping {scan_type} - No web services detected{Colors.END}")
            print(f"{Colors.CYAN}💡 Common web ports (80, 443) may not have been identified as web services{Colors.END}")
            print(f"{Colors.CYAN}💡 Try running whatweb or nikto manually if you suspect web services{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}🌐 Running {scan_type} on web ports: {web_ports}{Colors.END}")
        return True
    
    def test_web_port_responsiveness(self, target_ip: str, port: int) -> dict:
        """Test if a web port responds with actual content"""
        import subprocess
        import re
        
        protocols_to_test = []
        
        # Determine protocols to test based on port
        if port == 443 or port == 8443:
            protocols_to_test = ['https']
        elif port == 80:
            protocols_to_test = ['http']
        else:
            # For other ports, test both HTTP and HTTPS
            protocols_to_test = ['http', 'https']
        
        for protocol in protocols_to_test:
            url = f"{protocol}://{target_ip}:{port}"
            
            try:
                # Use curl to test responsiveness with a short timeout
                result = subprocess.run([
                    'curl', '-s', '-I', '--max-time', '5', '--connect-timeout', '3',
                    '-k',  # Allow insecure SSL
                    '--user-agent', 'ipsnipe/1.0.5',
                    url
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout:
                    # Check for valid HTTP response
                    if re.search(r'HTTP/\d+\.?\d*\s+\d{3}', result.stdout):
                        # Extract status code
                        status_match = re.search(r'HTTP/\d+\.?\d*\s+(\d{3})', result.stdout)
                        status_code = int(status_match.group(1)) if status_match else 0
                        
                        # Extract server header if present
                        server_match = re.search(r'Server:\s*(.+)', result.stdout, re.IGNORECASE)
                        server = server_match.group(1).strip() if server_match else "Unknown"
                        
                        return {
                            'responsive': True,
                            'url': url,
                            'status_code': status_code,
                            'server': server,
                            'protocol': protocol
                        }
                        
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
                continue
        
        return {'responsive': False, 'port': port}
    
    def get_best_web_port(self, target_ip: str, web_ports: List[int]) -> tuple:
        """Get the best responsive web port and URL"""
        if not web_ports:
            return None, None
        
        # Test responsiveness of web ports
        responsive_ports = []
        
        print(f"{Colors.YELLOW}🔍 Testing web port responsiveness...{Colors.END}")
        
        for port in web_ports[:5]:  # Test up to 5 ports to avoid delays
            result = self.test_web_port_responsiveness(target_ip, port)
            if result['responsive']:
                responsive_ports.append(result)
                print(f"{Colors.GREEN}✅ {result['url']} - {result['status_code']} ({result['server']}){Colors.END}")
        
        if not responsive_ports:
            print(f"{Colors.YELLOW}⚠️  No responsive web services found on tested ports{Colors.END}")
            # Return the first web port with HTTP as fallback
            return web_ports[0], f"http://{target_ip}:{web_ports[0]}"
        
        # Store responsive ports for later use
        self.responsive_web_ports = [p['url'] for p in responsive_ports]
        
        # Prefer HTTPS, then standard HTTP ports, then others
        def port_priority(port_info):
            port = int(port_info['url'].split(':')[-1])
            protocol = port_info['protocol']
            
            if protocol == 'https':
                return (0, port == 443, -port)  # HTTPS first, prefer 443
            else:
                return (1, port == 80, -port)   # HTTP second, prefer 80
        
        best_port_info = min(responsive_ports, key=port_priority)
        port = int(best_port_info['url'].split(':')[-1])
        
        print(f"{Colors.GREEN}🎯 Selected target: {best_port_info['url']}{Colors.END}")
        return port, best_port_info['url']
    
    def get_wordlist_path(self, wordlist_type: str) -> str:
        """Get the path to a wordlist file"""
        wordlist_config = self.config['wordlists']
        
        # Direct mapping
        if wordlist_type in wordlist_config:
            wordlist_path = wordlist_config[wordlist_type]
            if Path(wordlist_path).exists():
                return wordlist_path
        
        # Fallback options
        fallback_paths = [
            '/usr/share/wordlists/dirb/common.txt',
            '/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt',
            '/usr/share/seclists/Discovery/Web-Content/common.txt',
            '/opt/SecLists/Discovery/Web-Content/common.txt'
        ]
        
        for path in fallback_paths:
            if Path(path).exists():
                print(f"{Colors.YELLOW}⚠️  Using fallback wordlist: {path}{Colors.END}")
                return path
        
        # Create minimal wordlist as last resort
        return self.create_minimal_wordlist()
    
    def create_minimal_wordlist(self) -> str:
        """Create a minimal wordlist if none are found"""
        minimal_wordlist = [
            'admin', 'administrator', 'login', 'wp-admin', 'dashboard',
            'config', 'backup', 'test', 'api', 'robots.txt', 'sitemap.xml'
        ]
        
        wordlist_path = 'minimal_wordlist.txt'
        with open(wordlist_path, 'w') as f:
            f.write('\n'.join(minimal_wordlist))
        
        print(f"{Colors.YELLOW}⚠️  Created minimal wordlist: {wordlist_path}{Colors.END}")
        return wordlist_path
    
    def gobuster_common(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run Gobuster with common wordlist"""
        if not self.should_run_web_scan('Gobuster Common', web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        wordlist_path = self.get_wordlist_path('common')
        gobuster_config = self.config['gobuster']
        
        command = [
            'gobuster', 'dir',
            '-u', base_url,
            '-w', wordlist_path,
            '-x', gobuster_config['extensions'],
            '-t', str(gobuster_config['threads']),
            '--timeout', gobuster_config['timeout'],
            '-s', gobuster_config['status_codes'],
            '-q',  # Quiet mode
            '--no-error'
        ]
        
        if gobuster_config['include_length']:
            command.append('-l')
        
        if gobuster_config['follow_redirects']:
            command.append('-r')
        
        return run_command_func(command, 'gobuster_common.txt', 'Gobuster Directory Scan (Common)', 'gobuster')
    
    def gobuster_big(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run Gobuster with big wordlist"""
        if not self.should_run_web_scan('Gobuster Big', web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        wordlist_path = self.get_wordlist_path('big')
        gobuster_config = self.config['gobuster']
        
        command = [
            'gobuster', 'dir',
            '-u', base_url,
            '-w', wordlist_path,
            '-x', gobuster_config['extensions'],
            '-t', str(gobuster_config['threads']),
            '--timeout', gobuster_config['timeout'],
            '-s', gobuster_config['status_codes'],
            '-q',
            '--no-error'
        ]
        
        if gobuster_config['include_length']:
            command.append('-l')
        
        if gobuster_config['follow_redirects']:
            command.append('-r')
        
        return run_command_func(command, 'gobuster_big.txt', 'Gobuster Directory Scan (Big)', 'gobuster')
    
    def feroxbuster_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run Feroxbuster scan"""
        if not self.should_run_web_scan('Feroxbuster', web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        ferox_config = self.config['feroxbuster']
        wordlist_path = self.get_wordlist_path(ferox_config['wordlist_size'])
        
        command = [
            'feroxbuster',
            '-u', base_url,
            '-w', wordlist_path,
            '-x', ferox_config['extensions'],
            '-t', str(ferox_config['threads']),
            '--depth', str(ferox_config['depth']),
            '--timeout', str(ferox_config['timeout']),
            '-q'  # Quiet mode
        ]
        
        return run_command_func(command, 'feroxbuster.txt', 'Feroxbuster Directory Scan', 'feroxbuster')
    
    def ffuf_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run FFUF scan"""
        if not self.should_run_web_scan('FFUF', web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        ffuf_config = self.config['ffuf']
        wordlist_path = self.get_wordlist_path('common')
        
        command = [
            'ffuf',
            '-u', f"{base_url}/FUZZ",
            '-w', wordlist_path,
            '-e', ffuf_config['extensions'],
            '-t', str(ffuf_config['threads']),
            '-timeout', str(ffuf_config['timeout']),
            '-mc', ffuf_config['match_codes'],
            '-s'  # Silent mode
        ]
        
        if ffuf_config['filter_size']:
            command.extend(['-fs', ffuf_config['filter_size']])
        
        return run_command_func(command, 'ffuf.txt', 'FFUF Directory Scan', 'ffuf')
    
    def nikto_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run Nikto web vulnerability scan"""
        if not self.should_run_web_scan('Nikto', web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        nikto_config = self.config['nikto']
        
        command = [
            'nikto',
            '-h', base_url,
            '-Format', nikto_config['format'],
            '-timeout', str(nikto_config['timeout']),
            '-maxtime', str(nikto_config['max_scan_time'])
        ]
        
        return run_command_func(command, 'nikto.txt', 'Nikto Web Vulnerability Scan', 'nikto')
    
    def whatweb_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run WhatWeb technology detection"""
        if not self.should_run_web_scan('WhatWeb', web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        whatweb_config = self.config['whatweb']
        
        command = [
            'whatweb',
            '--log-brief=-',
            f'--aggression={whatweb_config["aggression"]}',
            '--no-errors',
            base_url
        ]
        
        if whatweb_config['verbosity'] == 'verbose':
            command.append('-v')
        
        return run_command_func(command, 'whatweb.txt', 'WhatWeb Technology Detection', 'whatweb') 