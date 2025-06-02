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
            
            # Pattern to match open ports from Nmap output
            # Matches lines like: "80/tcp   open  http"
            port_pattern = r'(\d+)/(tcp|udp)\s+open\s+(\S+)'
            matches = re.findall(port_pattern, content, re.IGNORECASE)
            
            newly_found_ports = []
            newly_found_web_ports = []
            
            for port_num, protocol, service in matches:
                port = int(port_num)
                
                # Add to open ports if not already there
                if port not in self.open_ports:
                    self.open_ports.append(port)
                    newly_found_ports.append(port)
                
                # Check if it's a web service
                web_services = [
                    'http', 'https', 'http-proxy', 'http-alt', 'https-alt',
                    'ssl/http', 'ssl/https', 'nginx', 'apache', 'lighttpd',
                    'tomcat', 'jetty', 'websphere', 'weblogic', 'iis'
                ]
                
                common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 9000, 3000, 5000]
                
                is_web_service = (
                    any(web_srv in service.lower() for web_srv in web_services) or
                    port in common_web_ports
                )
                
                if is_web_service and port not in self.web_ports:
                    self.web_ports.append(port)
                    newly_found_web_ports.append(port)
            
            # Sort the lists
            self.open_ports.sort()
            self.web_ports.sort()
            
            # Print discovery summary
            if newly_found_ports:
                print(f"{Colors.GREEN}🔍 Discovered {len(newly_found_ports)} open port(s): {newly_found_ports}{Colors.END}")
            
            if newly_found_web_ports:
                print(f"{Colors.CYAN}🌐 Identified {len(newly_found_web_ports)} web service(s): {newly_found_web_ports}{Colors.END}")
            
            # Advanced parsing for additional info
            self._parse_advanced_nmap_info(content)
            
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse Nmap output for port detection: {e}{Colors.END}")
    
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