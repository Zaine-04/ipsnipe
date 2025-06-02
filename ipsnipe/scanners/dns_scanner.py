#!/usr/bin/env python3
"""
DNS scanner implementations for ipsnipe
Handles theHarvester and dnsrecon scanning
"""

from typing import Dict
from ..ui.colors import Colors


class DNSScanner:
    """DNS and information gathering scanning functionality"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def theharvester_scan(self, target_ip: str, run_command_func) -> Dict:
        """Run theHarvester for email and subdomain enumeration"""
        # For IP targets, we need to try to get domain info first
        # This is a limitation - theHarvester works better with domains
        print(f"{Colors.YELLOW}ℹ️  theHarvester works best with domain names{Colors.END}")
        print(f"{Colors.CYAN}💡 Consider running this against the domain if you know it{Colors.END}")
        
        harvester_config = self.config['theharvester']
        
        # Try to use the IP as is, though results may be limited
        command = [
            'theHarvester',
            '-d', target_ip,
            '-b', harvester_config['data_source'],
            '-l', str(harvester_config['limit'])
        ]
        
        result = run_command_func(command, 'theharvester.txt', 'theHarvester Information Gathering', 'theharvester')
        
        # Add a note about domain usage in the result
        if result.get('status') == 'success':
            print(f"{Colors.CYAN}💡 For better results, run theHarvester manually with: theHarvester -d <domain> -b all{Colors.END}")
        
        return result
    
    def dnsrecon_scan(self, target_ip: str, run_command_func) -> Dict:
        """Run dnsrecon for DNS enumeration"""
        dnsrecon_config = self.config['dnsrecon']
        
        command = [
            'dnsrecon',
            '-r', f"{target_ip}/24",  # Reverse DNS lookup for the subnet
            '-t', dnsrecon_config['record_types'],
            '--threads', str(dnsrecon_config['threads'])
        ]
        
        result = run_command_func(command, 'dnsrecon.txt', 'DNSRecon DNS Enumeration', 'dnsrecon')
        
        # Also try direct IP lookup
        if result.get('status') == 'success':
            print(f"{Colors.CYAN}💡 Also performed reverse DNS lookup for {target_ip}/24 subnet{Colors.END}")
        
        return result 