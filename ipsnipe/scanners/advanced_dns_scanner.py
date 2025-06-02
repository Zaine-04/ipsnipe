#!/usr/bin/env python3
"""
Advanced DNS scanner with comprehensive enumeration techniques
Implements the most effective DNS discovery methods for HTB/CTF environments
"""

import subprocess
import re
import socket
import threading
import time
import json
import requests
from typing import Dict, List, Set, Optional, Tuple
from ..ui.colors import Colors

class AdvancedDNSScanner:
    """Advanced DNS enumeration with multiple techniques"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.discovered_subdomains = set()
        self.discovered_ips = set()
        self.dns_records = {}
        self.certificate_domains = set()
        self.historical_domains = set()
        
        # HTB-optimized subdomain wordlist
        self.htb_subdomains = [
            'admin', 'api', 'www', 'mail', 'ftp', 'vpn', 'ssh', 'remote',
            'portal', 'dev', 'test', 'staging', 'prod', 'app', 'blog',
            'forum', 'shop', 'store', 'secure', 'login', 'panel', 'dashboard',
            'manager', 'control', 'monitoring', 'backup', 'files', 'docs',
            'support', 'help', 'internal', 'private', 'secret', 'hidden',
            'db', 'database', 'mysql', 'postgres', 'redis', 'cache',
            'jenkins', 'gitlab', 'git', 'svn', 'ci', 'build', 'deploy',
            'ldap', 'ad', 'directory', 'auth', 'sso', 'oauth',
            'smtp', 'pop', 'imap', 'webmail', 'exchange',
            'ns', 'ns1', 'ns2', 'dns', 'resolver',
            'proxy', 'gateway', 'firewall', 'router',
            'media', 'static', 'assets', 'cdn', 'img', 'images',
            'mobile', 'app', 'api', 'm', 'wap',
            'old', 'legacy', 'archive', 'backup', 'bak'
        ]
    
    def comprehensive_enumeration(self, target_ip: str, discovered_domains: List[str], run_command_func) -> Dict:
        """Run comprehensive DNS enumeration with multiple techniques"""
        results = {
            'status': 'running',
            'techniques': {},
            'new_domains': set(),
            'dns_records': {},
            'certificate_domains': set(),
            'tools_used': []
        }
        
        print(f"\n{Colors.CYAN}🔍 Starting Advanced DNS Enumeration{Colors.END}")
        print(f"{Colors.YELLOW}📋 Target IP: {target_ip}{Colors.END}")
        print(f"{Colors.YELLOW}📋 Known Domains: {', '.join(discovered_domains)}{Colors.END}")
        
        if not discovered_domains:
            print(f"{Colors.YELLOW}⚠️  No domains available for enumeration{Colors.END}")
            results['status'] = 'completed'
            return results
        
        primary_domain = discovered_domains[0]
        
        # 1. Enhanced DNS Record Enumeration
        print(f"\n{Colors.GREEN}🎯 Phase 1: Enhanced DNS Record Enumeration{Colors.END}")
        dns_results = self._enhanced_dns_records(primary_domain, run_command_func)
        results['techniques']['dns_records'] = dns_results
        
        # 2. Subdomain Brute Force (HTB-optimized)
        print(f"\n{Colors.GREEN}🎯 Phase 2: HTB-Optimized Subdomain Discovery{Colors.END}")
        subdomain_results = self._htb_subdomain_bruteforce(primary_domain, run_command_func)
        results['techniques']['subdomain_brute'] = subdomain_results
        
        # 3. Certificate Transparency Logs
        print(f"\n{Colors.GREEN}🎯 Phase 3: Certificate Transparency Discovery{Colors.END}")
        cert_results = self._certificate_transparency(primary_domain)
        results['techniques']['certificate_transparency'] = cert_results
        
        # 4. DNS Zone Transfer Attempts
        print(f"\n{Colors.GREEN}🎯 Phase 4: Zone Transfer Attempts{Colors.END}")
        zone_results = self._zone_transfer_attempts(primary_domain, run_command_func)
        results['techniques']['zone_transfers'] = zone_results
        
        # 5. Reverse DNS Lookups
        print(f"\n{Colors.GREEN}🎯 Phase 5: Reverse DNS Analysis{Colors.END}")
        reverse_results = self._reverse_dns_analysis(target_ip, run_command_func)
        results['techniques']['reverse_dns'] = reverse_results
        
        # 6. Advanced Tools Integration
        print(f"\n{Colors.GREEN}🎯 Phase 6: Advanced Tools Integration{Colors.END}")
        tools_results = self._advanced_tools_enumeration(primary_domain, run_command_func)
        results['techniques']['advanced_tools'] = tools_results
        
        # Consolidate results
        all_domains = set()
        for technique_results in results['techniques'].values():
            if 'domains' in technique_results:
                all_domains.update(technique_results['domains'])
        
        # Filter out original domains to get only new discoveries
        original_domains_set = set(discovered_domains)
        new_domains = all_domains - original_domains_set
        
        results['new_domains'] = list(new_domains)
        results['total_domains'] = len(all_domains)
        results['new_count'] = len(new_domains)
        results['status'] = 'completed'
        
        # Summary
        print(f"\n{Colors.GREEN}✅ Advanced DNS Enumeration Complete{Colors.END}")
        print(f"{Colors.CYAN}📊 Results Summary:{Colors.END}")
        print(f"   • Total domains found: {len(all_domains)}")
        print(f"   • New domains: {len(new_domains)}")
        print(f"   • DNS records: {len(results['dns_records'])}")
        print(f"   • Certificate domains: {len(results['certificate_domains'])}")
        
        if new_domains:
            print(f"\n{Colors.YELLOW}🎯 New domains discovered:{Colors.END}")
            for domain in sorted(new_domains):
                print(f"   • {domain}")
        
        return results
    
    def _enhanced_dns_records(self, domain: str, run_command_func) -> Dict:
        """Enhanced DNS record enumeration with multiple record types"""
        results = {
            'domains': set(),
            'records': {},
            'nameservers': set()
        }
        
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SOA', 'SRV', 'PTR']
        
        for record_type in record_types:
            print(f"  🔍 Querying {record_type} records for {domain}")
            try:
                cmd = f"dig +short {record_type} {domain}"
                result = run_command_func(cmd, timeout=30)
                
                if result and result.get('success') and result.get('output'):
                    output = result['output'].strip()
                    if output and not output.startswith(';;'):
                        results['records'][record_type] = output.split('\n')
                        
                        # Extract domains from different record types
                        if record_type in ['CNAME', 'MX', 'NS']:
                            for line in output.split('\n'):
                                domain_match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
                                if domain_match:
                                    found_domain = domain_match.group(1).rstrip('.')
                                    results['domains'].add(found_domain)
                                    
                        if record_type == 'NS':
                            for line in output.split('\n'):
                                results['nameservers'].add(line.strip().rstrip('.'))
                        
            except Exception as e:
                print(f"    ❌ Error querying {record_type}: {e}")
        
        print(f"  ✅ Found {len(results['records'])} record types, {len(results['domains'])} domains")
        return results
    
    def _htb_subdomain_bruteforce(self, domain: str, run_command_func) -> Dict:
        """HTB-optimized subdomain brute force with common CTF patterns"""
        results = {
            'domains': set(),
            'valid_subdomains': [],
            'tested_count': 0
        }
        
        # Combine HTB-specific with common subdomains
        all_subdomains = self.htb_subdomains.copy()
        
        # Add common variations
        base_variations = ['dev', 'test', 'staging', 'prod', 'demo']
        for variation in base_variations:
            all_subdomains.extend([
                f"{variation}1", f"{variation}2", f"{variation}-api",
                f"api-{variation}", f"{variation}-web", f"web-{variation}"
            ])
        
        print(f"  🎯 Testing {len(all_subdomains)} HTB-optimized subdomains")
        
        # Batch DNS lookups for speed
        valid_subdomains = []
        for subdomain in all_subdomains:
            test_domain = f"{subdomain}.{domain}"
            results['tested_count'] += 1
            
            try:
                # Quick DNS resolution test
                socket.gethostbyname(test_domain)
                valid_subdomains.append(test_domain)
                results['domains'].add(test_domain)
                print(f"    ✅ {test_domain}")
                
            except socket.gaierror:
                # Subdomain doesn't exist, continue
                pass
            except Exception as e:
                # Other error, continue but note it
                pass
        
        results['valid_subdomains'] = valid_subdomains
        print(f"  ✅ Found {len(valid_subdomains)} valid subdomains from {results['tested_count']} tests")
        
        return results
    
    def _certificate_transparency(self, domain: str) -> Dict:
        """Search certificate transparency logs for subdomains"""
        results = {
            'domains': set(),
            'certificates': [],
            'sources': []
        }
        
        # crt.sh API (most reliable for CTFs)
        try:
            print(f"  🔍 Searching crt.sh for {domain}")
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                certs = response.json()
                results['sources'].append('crt.sh')
                
                for cert in certs:
                    if 'name_value' in cert:
                        names = cert['name_value'].split('\n')
                        for name in names:
                            name = name.strip().lower()
                            # Filter out wildcards and add valid domains
                            if '.' in name and not name.startswith('*'):
                                results['domains'].add(name)
                
                print(f"    ✅ Found {len(results['domains'])} domains from certificates")
                
        except Exception as e:
            print(f"    ❌ Certificate transparency search failed: {e}")
        
        return results
    
    def _zone_transfer_attempts(self, domain: str, run_command_func) -> Dict:
        """Attempt DNS zone transfers against discovered nameservers"""
        results = {
            'domains': set(),
            'transfers': {},
            'nameservers_tested': []
        }
        
        # Get nameservers for the domain
        nameservers = set()
        try:
            cmd = f"dig +short NS {domain}"
            result = run_command_func(cmd, timeout=30)
            if result and result.get('success') and result.get('output'):
                for ns in result['output'].strip().split('\n'):
                    if ns.strip():
                        nameservers.add(ns.strip().rstrip('.'))
        except Exception:
            pass
        
        # Also try common nameserver patterns
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            base_domain = '.'.join(domain_parts[-2:])
            nameservers.update([
                f"ns1.{base_domain}", f"ns2.{base_domain}", f"ns.{base_domain}",
                f"dns1.{base_domain}", f"dns2.{base_domain}", f"dns.{base_domain}"
            ])
        
        print(f"  🎯 Testing zone transfers against {len(nameservers)} nameservers")
        
        for ns in nameservers:
            results['nameservers_tested'].append(ns)
            try:
                print(f"    🔍 Attempting zone transfer from {ns}")
                cmd = f"dig @{ns} {domain} AXFR"
                result = run_command_func(cmd, timeout=60)
                
                if result and result.get('success') and result.get('output'):
                    output = result['output']
                    
                    # Check if zone transfer was successful
                    if 'Transfer failed' not in output and 'connection timed out' not in output:
                        # Extract domains from zone transfer
                        domain_pattern = r'([a-zA-Z0-9.-]+\.' + re.escape(domain) + r')'
                        domains_found = re.findall(domain_pattern, output)
                        
                        if domains_found:
                            results['transfers'][ns] = domains_found
                            results['domains'].update(domains_found)
                            print(f"      ✅ Zone transfer successful! Found {len(domains_found)} domains")
                        else:
                            print(f"      ❌ Zone transfer denied")
                    else:
                        print(f"      ❌ Zone transfer failed")
                        
            except Exception as e:
                print(f"      ❌ Error with {ns}: {e}")
        
        return results
    
    def _reverse_dns_analysis(self, target_ip: str, run_command_func) -> Dict:
        """Perform reverse DNS analysis on target IP and nearby IPs"""
        results = {
            'domains': set(),
            'ip_domains': {},
            'ip_range_tested': []
        }
        
        # Parse target IP for range analysis
        try:
            ip_parts = target_ip.split('.')
            if len(ip_parts) == 4:
                base_ip = '.'.join(ip_parts[:3])
                target_last_octet = int(ip_parts[3])
                
                # Test nearby IPs (common in CTF environments)
                test_range = []
                for offset in [-10, -5, -2, -1, 0, 1, 2, 5, 10]:
                    test_octet = target_last_octet + offset
                    if 1 <= test_octet <= 254:
                        test_range.append(f"{base_ip}.{test_octet}")
                
                print(f"  🎯 Testing reverse DNS for {len(test_range)} nearby IPs")
                
                for test_ip in test_range:
                    results['ip_range_tested'].append(test_ip)
                    try:
                        cmd = f"dig +short -x {test_ip}"
                        result = run_command_func(cmd, timeout=10)
                        
                        if result and result.get('success') and result.get('output'):
                            domain = result['output'].strip().rstrip('.')
                            if domain and '.' in domain:
                                results['domains'].add(domain)
                                results['ip_domains'][test_ip] = domain
                                print(f"    ✅ {test_ip} -> {domain}")
                                
                    except Exception:
                        pass
        
        except Exception as e:
            print(f"    ❌ Reverse DNS analysis error: {e}")
        
        return results
    
    def _advanced_tools_enumeration(self, domain: str, run_command_func) -> Dict:
        """Use advanced enumeration tools if available"""
        results = {
            'domains': set(),
            'tools_used': [],
            'tool_results': {}
        }
        
        # 1. Try Subfinder (if available)
        try:
            print(f"  🔍 Testing Subfinder availability")
            test_cmd = "subfinder -version"
            test_result = run_command_func(test_cmd, timeout=10)
            
            if test_result and test_result.get('success'):
                print(f"  🎯 Running Subfinder against {domain}")
                cmd = f"subfinder -d {domain} -silent -t 20"
                result = run_command_func(cmd, timeout=300)
                
                if result and result.get('success') and result.get('output'):
                    subdomains = [line.strip() for line in result['output'].split('\n') if line.strip()]
                    results['domains'].update(subdomains)
                    results['tool_results']['subfinder'] = subdomains
                    results['tools_used'].append('subfinder')
                    print(f"    ✅ Subfinder found {len(subdomains)} subdomains")
                    
        except Exception as e:
            print(f"    ❌ Subfinder error: {e}")
        
        # 2. Try DNSRecon (if available)
        try:
            print(f"  🔍 Testing DNSRecon availability")
            test_cmd = "dnsrecon -h"
            test_result = run_command_func(test_cmd, timeout=10)
            
            if test_result and test_result.get('success'):
                print(f"  🎯 Running DNSRecon against {domain}")
                cmd = f"dnsrecon -d {domain} -t std,brt"
                result = run_command_func(cmd, timeout=300)
                
                if result and result.get('success') and result.get('output'):
                    # Parse DNSRecon output for domains
                    domain_pattern = r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                    found_domains = re.findall(domain_pattern, result['output'])
                    filtered_domains = [d for d in found_domains if domain in d]
                    
                    results['domains'].update(filtered_domains)
                    results['tool_results']['dnsrecon'] = filtered_domains
                    results['tools_used'].append('dnsrecon')
                    print(f"    ✅ DNSRecon found {len(filtered_domains)} domains")
                    
        except Exception as e:
            print(f"    ❌ DNSRecon error: {e}")
        
        # 3. Try Amass (if available)
        try:
            print(f"  🔍 Testing Amass availability")
            test_cmd = "amass -version"
            test_result = run_command_func(test_cmd, timeout=10)
            
            if test_result and test_result.get('success'):
                print(f"  🎯 Running Amass against {domain}")
                cmd = f"amass enum -passive -d {domain} -timeout 5"
                result = run_command_func(cmd, timeout=300)
                
                if result and result.get('success') and result.get('output'):
                    subdomains = [line.strip() for line in result['output'].split('\n') 
                                if line.strip() and domain in line.strip()]
                    results['domains'].update(subdomains)
                    results['tool_results']['amass'] = subdomains
                    results['tools_used'].append('amass')
                    print(f"    ✅ Amass found {len(subdomains)} subdomains")
                    
        except Exception as e:
            print(f"    ❌ Amass error: {e}")
        
        if results['tools_used']:
            print(f"  ✅ Advanced tools used: {', '.join(results['tools_used'])}")
        else:
            print(f"  ℹ️  No advanced DNS tools available")
        
        return results 