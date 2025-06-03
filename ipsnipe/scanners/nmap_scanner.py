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
        """Run aggressive full Nmap scan with high min-rate using configuration or custom port range"""
        nmap_config = self.config['nmap']
        
        # Determine scan type based on sudo mode for maximum speed
        if self.enhanced_mode:
            command = ['sudo', 'nmap', '-sS']  # SYN scan with sudo for speed
            scan_description = 'Nmap Aggressive Full Scan (Enhanced SYN + High Min-Rate)'
        else:
            command = ['nmap', '-sT']  # TCP connect scan
            scan_description = 'Nmap Aggressive Full Scan (Standard TCP + High Min-Rate)'
        
        # Add high min-rate for aggressive scanning (HTB optimized)
        if 'min_rate' in nmap_config:
            command.extend(['--min-rate', str(nmap_config['min_rate'])])
        
        if nmap_config['enable_version_detection']:
            command.extend(['-sV', '--version-intensity', str(nmap_config['version_intensity'])])
        
        # Only enable OS detection in enhanced mode
        if nmap_config['enable_os_detection'] and self.enhanced_mode:
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
        
        result = run_command_func(command, 'nmap_full.txt', scan_description, 'nmap')
        
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
        
        # Add high min-rate for aggressive UDP scanning (HTB optimized)
        if 'min_rate' in nmap_config:
            command.extend(['--min-rate', str(nmap_config['min_rate'])])
        
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
            
            # Enhanced patterns to catch different nmap output formats
            patterns = [
                r'(\d+)/(tcp|udp)\s+open\s+(\S+)',  # Standard format: "80/tcp   open  http"
                r'(\d+)/(tcp|udp)\s+open\s+(\S+.*?)(?:\s|$)',  # With additional info
                r'PORT\s+STATE\s+SERVICE.*?(\d+)/(tcp|udp)\s+open\s+(\S+)',  # Table format
                r'^(\d+)/(tcp|udp)\s+open\s+(.+?)$',  # Line-by-line parsing
            ]
            
            all_matches = []
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    print(f"{Colors.CYAN}   Pattern {i+1} found {len(matches)} matches{Colors.END}")
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
            
            # If no matches found, let's look for open ports manually
            if not unique_matches:
                print(f"{Colors.YELLOW}⚠️  No regex matches found, trying manual port detection...{Colors.END}")
                # Look for lines that contain "open" and port numbers
                lines = content.split('\n')
                for line in lines:
                    if 'open' in line.lower() and re.search(r'\d+/(tcp|udp)', line):
                        print(f"{Colors.CYAN}   Debug line: {line.strip()}{Colors.END}")
                        # Try to extract port manually
                        port_match = re.search(r'(\d+)/(tcp|udp)', line)
                        if port_match:
                            port = int(port_match.group(1))
                            protocol = port_match.group(2)
                            unique_matches.append((str(port), protocol, 'unknown'))
            
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
                    common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 9000, 3000, 5000, 8008, 8181, 9090]
                    
                    # More aggressive web service detection
                    is_web_service = (
                        port in common_web_ports or  # Always consider common web ports
                        any(web_srv in service.lower() for web_srv in web_services) or
                        'ssl' in service.lower() or  # SSL often indicates HTTPS
                        service.lower() in ['unknown', 'tcpwrapped']  # Unknown services on web ports might be web
                    )
                    
                    if is_web_service and port not in self.web_ports:
                        self.web_ports.append(port)
                        newly_found_web_ports.append(port)
                        print(f"{Colors.GREEN}   → Classified as web service{Colors.END}")
            
            # IMPORTANT: Force classification of port 80 and 443 if they're open but not detected as web
            for common_port in [80, 443]:
                if common_port in self.open_ports and common_port not in self.web_ports:
                    self.web_ports.append(common_port)
                    newly_found_web_ports.append(common_port)
                    print(f"{Colors.GREEN}🔧 Force-classified port {common_port} as web service (common web port){Colors.END}")
            
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
                # Additional fallback check
                if any(port in [80, 443, 8080, 8443] for port in self.open_ports):
                    print(f"{Colors.CYAN}🔧 Found common web ports in open ports, adding to web services...{Colors.END}")
                    for port in [80, 443, 8080, 8443]:
                        if port in self.open_ports and port not in self.web_ports:
                            self.web_ports.append(port)
                            print(f"{Colors.GREEN}   Added port {port} as web service{Colors.END}")
                    self.web_ports.sort()
                else:
                    print(f"{Colors.CYAN}💡 Web scanners will be skipped. Run manual tests if you suspect web services.{Colors.END}")
            
            # Show final port summary
            print(f"{Colors.BLUE}📊 Final summary: {len(self.open_ports)} open ports, {len(self.web_ports)} web services{Colors.END}")
            if self.web_ports:
                print(f"{Colors.CYAN}   Web ports: {self.web_ports}{Colors.END}")
            
            # Advanced parsing for additional info
            self._parse_advanced_nmap_info(content)
            
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse Nmap output for port detection: {e}{Colors.END}")
            # Enhanced fallback: if we can't parse, assume common web ports are web services
            print(f"{Colors.CYAN}🔧 Activating enhanced fallback web service detection...{Colors.END}")
            
            # Try to find any open ports from the file content
            try:
                with open(output_file, 'r') as f:
                    content = f.read()
                
                # Look for port numbers in the content
                potential_ports = re.findall(r'(\d+)/(tcp|udp)', content)
                if potential_ports:
                    for port_str, proto in potential_ports:
                        port = int(port_str)
                        if port not in self.open_ports:
                            self.open_ports.append(port)
                    print(f"{Colors.GREEN}   Found potential ports: {[int(p[0]) for p in potential_ports]}{Colors.END}")
                
            except:
                pass
            
            # Force common web ports as web services
            for port in [80, 443, 8080, 8443]:
                if port in self.open_ports and port not in self.web_ports:
                    self.web_ports.append(port)
                    print(f"{Colors.YELLOW}🔄 Fallback: Adding port {port} as web service{Colors.END}")
            
            self.open_ports.sort()
            self.web_ports.sort()
    
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
    
    def domain_enhanced_scan(self, domain: str, run_command_func, port_list: str) -> Dict:
        """Run enhanced nmap scan using domain name for better service detection"""
        
        # Build enhanced nmap command with domain
        command = ['nmap']
        
        if self.enhanced_mode:
            command.extend(['-sS', '-O'])  # SYN scan with OS detection
        else:
            command.extend(['-sT'])  # TCP connect scan
        
        # Add service detection and version scanning
        command.extend([
            '-sV',  # Service version detection
            '-sC',  # Default scripts
            '--script=http-title,http-headers,ssl-cert,ssl-enum-ciphers',  # Specific scripts for web/ssl
            '-p', port_list,
            domain
        ])
        
        output_file = f"nmap_domain_enhanced_{domain.replace('.', '_')}.txt"
        
        print(f"{Colors.CYAN}🔍 Running enhanced nmap scan on {domain} (ports: {port_list})...{Colors.END}")
        
        result = run_command_func(command, output_file, f"Enhanced nmap scan on {domain}", "nmap")
        
        # If successful, parse the results for better service information
        if result.get('status') == 'success':
            # Parse the output to update service information
            try:
                output_path = f"{run_command_func.__self__.scanner_core.output_dir}/{output_file}"
                with open(output_path, 'r') as f:
                    content = f.read()
                    
                print(f"{Colors.GREEN}📄 Enhanced scan results:{Colors.END}")
                
                # Look for enhanced service information
                lines = content.split('\n')
                
                for line in lines:
                    # Look for HTTP titles
                    if 'http-title:' in line:
                        title_match = re.search(r'http-title:\s*(.+)', line)
                        if title_match:
                            title = title_match.group(1).strip()
                            print(f"{Colors.GREEN}   📄 HTTP Title: {title}{Colors.END}")
                    
                    # Look for SSL certificate info
                    elif 'ssl-cert:' in line and 'Subject:' in line:
                        print(f"{Colors.CYAN}   🔒 SSL Certificate info found{Colors.END}")
                    
                    # Look for interesting HTTP headers
                    elif 'Server:' in line:
                        print(f"{Colors.BLUE}   🖥️  {line.strip()}{Colors.END}")
                
                print(f"{Colors.GREEN}✅ Enhanced domain scan completed with additional service details{Colors.END}")
                
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Could not parse enhanced scan results: {str(e)}{Colors.END}")
        
        return result 