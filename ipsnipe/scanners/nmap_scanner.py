#!/usr/bin/env python3
"""
Nmap scanner implementation for ipsnipe
Handles all Nmap-related scanning functionality
"""

import re
from typing import Dict, List, Optional
from pathlib import Path
from ..ui.colors import Colors


class NmapScanner:
    """Nmap scanning functionality"""
    
    def __init__(self, config: Dict, enhanced_mode: bool = False):
        self.config = config
        self.enhanced_mode = enhanced_mode
        self.open_ports = []
        self.web_ports = []
    
    def quick_scan(self, target_ip: str, run_command_func, port_range: Optional[str] = None) -> Dict:
        """Run quick Nmap scan using configuration or custom port range"""
        nmap_config = self.config['nmap']
        
        # Determine scan type based on sudo mode
        if self.enhanced_mode:
            command = ['sudo', 'nmap', '-sS']  # SYN scan with sudo
            scan_description = 'Nmap Quick Scan (Enhanced SYN)'
        else:
            command = ['nmap', '-sT']  # TCP connect scan
            scan_description = 'Nmap Quick Scan (Standard TCP)'
        
        if nmap_config['enable_version_detection']:
            command.extend(['-sV', '--version-intensity', str(nmap_config['version_intensity'])])
        
        # Only enable OS detection in enhanced mode
        if nmap_config['enable_os_detection'] and self.enhanced_mode:
            command.append('-O')
        
        # Use custom port range if provided, otherwise use default
        if port_range and port_range != 'default':
            if ',' in port_range or '-' in port_range:
                command.extend(['-p', port_range])
            else:
                command.extend(['-p', port_range])
        else:
            command.extend(['--top-ports', str(nmap_config['quick_ports'])])
        
        command.extend([f'-{nmap_config["timing"]}', target_ip])
        
        result = run_command_func(command, 'nmap_quick.txt', scan_description, 'nmap')
        
        # Parse output for port detection if scan was successful
        if result['status'] == 'success':
            self.parse_nmap_output_for_ports(result['output_file'])
        
        return result
    
    def full_scan(self, target_ip: str, run_command_func, port_range: Optional[str] = None) -> Dict:
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
        
        command.append(target_ip)
        
        result = run_command_func(command, 'nmap_full.txt', 'Nmap Full Scan', 'nmap')
        
        # Parse output for port detection if scan was successful
        if result['status'] == 'success':
            self.parse_nmap_output_for_ports(result['output_file'])
        
        return result
    
    def udp_scan(self, target_ip: str, run_command_func, port_range: Optional[str] = None) -> Dict:
        """Run UDP Nmap scan using configuration or custom port range"""
        # UDP scans require root privileges
        if not self.enhanced_mode:
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
        
        command.extend([f'-{nmap_config["timing"]}', target_ip])
        
        result = run_command_func(command, 'nmap_udp.txt', 'Nmap UDP Scan', 'nmap')
        
        # Parse output for port detection if scan was successful
        if result['status'] == 'success':
            self.parse_nmap_output_for_ports(result['output_file'])
        
        return result
    
    def parse_nmap_output_for_ports(self, output_file: str) -> None:
        """Parse Nmap output to extract open ports and identify web services"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            print(f"{Colors.BLUE}🔍 Parsing nmap output for port detection...{Colors.END}")
            
            # Multiple patterns to catch different nmap output formats
            patterns = [
                r'(\d+)/(tcp|udp)\s+open\s+(\S+)',  # Standard format: "80/tcp   open  http"
                r'(\d+)/(tcp|udp)\s+open\s+(\S+.*)',  # With additional info
                r'PORT\s+STATE\s+SERVICE.*?(\d+)/(tcp|udp)\s+open\s+(\S+)',  # Table format
            ]
            
            all_matches = []
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                all_matches.extend(matches)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_matches = []
            for match in all_matches:
                if len(match) >= 3:
                    key = (match[0], match[1])
                    if key not in seen:
                        seen.add(key)
                        unique_matches.append(match)
            
            newly_found_ports = []
            newly_found_web_ports = []
            
            print(f"{Colors.YELLOW}📝 Raw matches found: {len(unique_matches)}{Colors.END}")
            
            for match in unique_matches:
                if len(match) >= 3:
                    port_num, protocol, service = match[0], match[1], match[2]
                    port = int(port_num)
                    
                    print(f"{Colors.CYAN}   Port {port}/{protocol} -> {service}{Colors.END}")
                    
                    # Add to open ports if not already there
                    if port not in self.open_ports:
                        self.open_ports.append(port)
                        newly_found_ports.append(port)
                    
                    # Enhanced web service detection
                    web_services = [
                        'http', 'https', 'http-proxy', 'http-alt', 'https-alt',
                        'ssl/http', 'ssl/https', 'nginx', 'apache', 'lighttpd',
                        'tomcat', 'jetty', 'websphere', 'weblogic', 'iis',
                        'httpd', 'www', 'web', 'ssl', 'tls'
                    ]
                    
                    # Common web ports (always consider these as web services)
                    common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 9000, 3000, 5000, 8008, 8181, 8888, 9090]
                    
                    # More aggressive web service detection
                    is_web_service = (
                        port in common_web_ports or  # Always consider common web ports
                        any(web_srv in service.lower() for web_srv in web_services) or
                        'ssl' in service.lower() or  # SSL often indicates HTTPS
                        service.lower() in ['unknown', 'tcpwrapped']  # Unknown services on web ports
                    )
                    
                    if is_web_service and port not in self.web_ports:
                        self.web_ports.append(port)
                        newly_found_web_ports.append(port)
                        print(f"{Colors.GREEN}   → Classified as web service{Colors.END}")
            
            # Sort the lists
            self.open_ports.sort()
            self.web_ports.sort()
            
            # Print discovery summary
            if newly_found_ports:
                print(f"{Colors.GREEN}🔍 Discovered {len(newly_found_ports)} open port(s): {newly_found_ports}{Colors.END}")
            
            if newly_found_web_ports:
                print(f"{Colors.CYAN}🌐 Identified {len(newly_found_web_ports)} web service(s): {newly_found_web_ports}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  No web services detected from nmap output{Colors.END}")
                print(f"{Colors.CYAN}💡 Web scanners will be skipped. Run manual tests if you suspect web services.{Colors.END}")
            
            # Advanced parsing for additional info
            self._parse_advanced_nmap_info(content)
            
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse Nmap output for port detection: {e}{Colors.END}")
            # Fallback: if we can't parse, assume common web ports are web services
            if 80 in self.open_ports and 80 not in self.web_ports:
                self.web_ports.append(80)
                print(f"{Colors.YELLOW}🔄 Fallback: Adding port 80 as web service{Colors.END}")
            if 443 in self.open_ports and 443 not in self.web_ports:
                self.web_ports.append(443)
                print(f"{Colors.YELLOW}🔄 Fallback: Adding port 443 as web service{Colors.END}")
    
    def _parse_advanced_nmap_info(self, content: str) -> None:
        """Parse additional information from Nmap output"""
        # Look for OS detection results
        os_pattern = r'OS details: (.+)'
        os_matches = re.findall(os_pattern, content)
        if os_matches:
            print(f"{Colors.BLUE}🖥️  OS Detection: {os_matches[0]}{Colors.END}")
        
        # Look for service versions
        version_pattern = r'(\d+)/(tcp|udp)\s+open\s+\S+\s+(.+)'
        version_matches = re.findall(version_pattern, content)
        
        interesting_services = []
        for port, protocol, version_info in version_matches:
            if len(version_info.strip()) > 10:  # Detailed version info
                interesting_services.append(f"Port {port}: {version_info.strip()}")
        
        if interesting_services and len(interesting_services) <= 5:  # Don't spam too many
            print(f"{Colors.PURPLE}🔬 Service Details:{Colors.END}")
            for service in interesting_services[:3]:  # Show max 3
                print(f"   {service}")
    
    def get_open_ports(self) -> List[int]:
        """Get list of discovered open ports"""
        return self.open_ports.copy()
    
    def get_web_ports(self) -> List[int]:
        """Get list of discovered web service ports"""
        return self.web_ports.copy()
    
    def has_web_services(self) -> bool:
        """Check if any web services were discovered"""
        return len(self.web_ports) > 0
    
    def force_add_web_ports(self, ports: List[int]) -> None:
        """Manually add ports as web services (useful for edge cases)"""
        for port in ports:
            if port in self.open_ports and port not in self.web_ports:
                self.web_ports.append(port)
                print(f"{Colors.GREEN}🔧 Manually added port {port} as web service{Colors.END}")
        self.web_ports.sort()
    
    def detect_web_services_by_response(self, target_ip: str) -> None:
        """Try to detect web services by actually testing HTTP/HTTPS responses"""
        import subprocess
        
        print(f"{Colors.YELLOW}🔍 Testing open ports for web services...{Colors.END}")
        
        potential_web_ports = []
        for port in self.open_ports[:10]:  # Test up to 10 ports
            # Test HTTP
            try:
                result = subprocess.run([
                    'curl', '-s', '-I', '--max-time', '3', '--connect-timeout', '2',
                    f'http://{target_ip}:{port}'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and 'HTTP/' in result.stdout:
                    potential_web_ports.append(port)
                    print(f"{Colors.GREEN}   HTTP response on port {port}{Colors.END}")
            except:
                pass
            
            # Test HTTPS
            try:
                result = subprocess.run([
                    'curl', '-s', '-I', '--max-time', '3', '--connect-timeout', '2', '-k',
                    f'https://{target_ip}:{port}'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and 'HTTP/' in result.stdout:
                    if port not in potential_web_ports:
                        potential_web_ports.append(port)
                        print(f"{Colors.GREEN}   HTTPS response on port {port}{Colors.END}")
            except:
                pass
        
        # Add detected web ports
        for port in potential_web_ports:
            if port not in self.web_ports:
                self.web_ports.append(port)
        
        self.web_ports.sort()
        
        if potential_web_ports:
            print(f"{Colors.CYAN}🌐 Detected web services by response testing: {potential_web_ports}{Colors.END}") 