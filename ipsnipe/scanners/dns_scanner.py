#!/usr/bin/env python3
"""
DNS scanner implementations for ipsnipe
Handles theHarvester scanning and comprehensive dig-based DNS enumeration
"""

import subprocess
import re
import socket
from typing import Dict, List, Set, Optional, Tuple
from ..ui.colors import Colors


class DNSScanner:
    """DNS and information gathering scanning functionality"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.discovered_domains = set()
        self.discovered_subdomains = set()
        self.dns_records = {}
    
    def comprehensive_dns_enumeration(self, target_ip: str, discovered_domains: List[str], run_command_func) -> Dict:
        """
        Comprehensive DNS enumeration using dig
        Includes zone transfers, subdomain discovery, wildcard detection
        """
        if not discovered_domains:
            print(f"{Colors.YELLOW}⏭️  Skipping DNS enumeration - no domains discovered yet{Colors.END}")
            return {'status': 'skipped', 'reason': 'No domains available for DNS enumeration'}
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Comprehensive DNS Enumeration{Colors.END}")
        print("-" * 60)
        print(f"{Colors.GREEN}🎯 Target domains: {discovered_domains}{Colors.END}")
        
        all_results = {
            'zone_transfers': {},
            'subdomains': set(),
            'dns_records': {},
            'wildcards': {},
            'nameservers': {},
            'reverse_dns': {}
        }
        
        for domain in discovered_domains:
            print(f"\n{Colors.CYAN}🌐 Enumerating DNS for domain: {domain}{Colors.END}")
            
            # 1. Zone Transfer Attempts
            zone_result = self._attempt_zone_transfer(domain)
            if zone_result['success']:
                all_results['zone_transfers'][domain] = zone_result
                all_results['subdomains'].update(zone_result.get('subdomains', []))
            
            # 2. DNS Record Enumeration
            dns_records = self._enumerate_dns_records(domain)
            all_results['dns_records'][domain] = dns_records
            
            # 3. Nameserver Discovery
            nameservers = self._discover_nameservers(domain)
            all_results['nameservers'][domain] = nameservers
            
            # 4. Subdomain Brute Force
            brute_subdomains = self._brute_force_subdomains(domain)
            all_results['subdomains'].update(brute_subdomains)
            
            # 5. Wildcard Detection
            wildcard_result = self._detect_wildcards(domain)
            all_results['wildcards'][domain] = wildcard_result
            
            # 6. Reverse DNS on target IP
            reverse_result = self._reverse_dns_lookup(target_ip)
            all_results['reverse_dns'][target_ip] = reverse_result
        
        # Convert sets to lists for JSON serialization
        all_results['subdomains'] = list(all_results['subdomains'])
        
        # Save comprehensive results
        self._save_dns_results(all_results, run_command_func)
        
        # Return discovered subdomains for hosts file addition
        new_domains = list(all_results['subdomains'])
        if new_domains:
            print(f"\n{Colors.GREEN}🎉 DNS enumeration discovered {len(new_domains)} new subdomains{Colors.END}")
            print(f"{Colors.CYAN}📝 New domains: {new_domains}{Colors.END}")
            return {
                'status': 'success',
                'new_domains': new_domains,
                'dns_results': all_results,
                'output_file': 'dns_enumeration.txt'
            }
        else:
            print(f"\n{Colors.YELLOW}ℹ️  DNS enumeration completed - no new subdomains discovered{Colors.END}")
            return {
                'status': 'success',
                'new_domains': [],
                'dns_results': all_results,
                'output_file': 'dns_enumeration.txt'
            }
    
    def _attempt_zone_transfer(self, domain: str) -> Dict:
        """Attempt DNS zone transfer (AXFR) on the domain"""
        print(f"{Colors.YELLOW}🔄 Attempting zone transfer for {domain}...{Colors.END}")
        
        # First get nameservers
        nameservers = self._get_nameservers(domain)
        if not nameservers:
            print(f"{Colors.YELLOW}   ⚠️  No nameservers found for {domain}{Colors.END}")
            return {'success': False, 'reason': 'No nameservers found'}
        
        subdomains = set()
        successful_transfers = []
        
        for ns in nameservers:
            print(f"{Colors.CYAN}   🎯 Trying zone transfer from {ns}...{Colors.END}")
            
            try:
                # Attempt AXFR
                result = subprocess.run([
                    'dig', 'axfr', domain, f'@{ns}'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout:
                    # Check if transfer was successful (not refused)
                    if 'Transfer failed' not in result.stdout and 'refused' not in result.stdout.lower():
                        print(f"{Colors.GREEN}   ✅ Zone transfer successful from {ns}!{Colors.END}")
                        successful_transfers.append(ns)
                        
                        # Parse subdomains from zone transfer
                        for line in result.stdout.split('\n'):
                            if line.strip() and not line.startswith(';'):
                                # Extract subdomain from DNS record
                                parts = line.split()
                                if len(parts) >= 1:
                                    subdomain = parts[0].rstrip('.')
                                    if subdomain.endswith(f'.{domain}'):
                                        full_subdomain = subdomain
                                    elif subdomain != domain and '.' in subdomain:
                                        full_subdomain = f"{subdomain}.{domain}"
                                    else:
                                        continue
                                    
                                    if full_subdomain != domain:
                                        subdomains.add(full_subdomain)
                                        print(f"{Colors.GREEN}     📍 Found: {full_subdomain}{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}   ⚠️  Zone transfer refused by {ns}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}   ⚠️  Zone transfer failed for {ns}{Colors.END}")
                    
            except subprocess.TimeoutExpired:
                print(f"{Colors.YELLOW}   ⏰ Zone transfer timed out for {ns}{Colors.END}")
            except Exception as e:
                print(f"{Colors.YELLOW}   ⚠️  Error with {ns}: {str(e)}{Colors.END}")
        
        if successful_transfers:
            return {
                'success': True,
                'nameservers': successful_transfers,
                'subdomains': list(subdomains),
                'count': len(subdomains)
            }
        else:
            print(f"{Colors.YELLOW}   ❌ All zone transfer attempts failed{Colors.END}")
            return {'success': False, 'reason': 'Zone transfers refused or failed'}
    
    def _get_nameservers(self, domain: str) -> List[str]:
        """Get nameservers for a domain"""
        try:
            result = subprocess.run([
                'dig', 'NS', domain, '+short'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                nameservers = []
                for line in result.stdout.strip().split('\n'):
                    ns = line.strip().rstrip('.')
                    if ns and '.' in ns:
                        nameservers.append(ns)
                return nameservers
        except Exception:
            pass
        return []
    
    def _enumerate_dns_records(self, domain: str) -> Dict:
        """Enumerate various DNS record types"""
        print(f"{Colors.YELLOW}📊 Enumerating DNS records for {domain}...{Colors.END}")
        
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SOA', 'SRV']
        records = {}
        
        for record_type in record_types:
            try:
                result = subprocess.run([
                    'dig', record_type, domain, '+short'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    records[record_type] = result.stdout.strip().split('\n')
                    print(f"{Colors.GREEN}   ✅ {record_type}: {len(records[record_type])} record(s){Colors.END}")
                    
                    # Look for subdomains in CNAME records
                    if record_type == 'CNAME':
                        for cname in records[record_type]:
                            cname = cname.rstrip('.')
                            if cname.endswith(f'.{domain}') and cname != domain:
                                self.discovered_subdomains.add(cname)
                
            except Exception as e:
                print(f"{Colors.YELLOW}   ⚠️  Failed to get {record_type} records: {str(e)}{Colors.END}")
        
        return records
    
    def _discover_nameservers(self, domain: str) -> List[str]:
        """Discover nameservers and try zone transfers"""
        nameservers = self._get_nameservers(domain)
        if nameservers:
            print(f"{Colors.GREEN}   🌐 Nameservers: {nameservers}{Colors.END}")
        return nameservers
    
    def _brute_force_subdomains(self, domain: str) -> Set[str]:
        """Brute force common subdomains"""
        print(f"{Colors.YELLOW}🔨 Brute forcing common subdomains for {domain}...{Colors.END}")
        
        # Common subdomain list
        common_subdomains = [
            'www', 'mail', 'email', 'webmail', 'admin', 'administrator', 'ftp', 'sftp',
            'ssh', 'vpn', 'api', 'app', 'apps', 'blog', 'dev', 'test', 'stage', 'staging',
            'prod', 'production', 'beta', 'alpha', 'demo', 'portal', 'shop', 'store',
            'login', 'panel', 'dashboard', 'control', 'manage', 'management', 'support',
            'help', 'docs', 'documentation', 'wiki', 'forum', 'forums', 'chat',
            'ns1', 'ns2', 'dns1', 'dns2', 'mx1', 'mx2', 'smtp', 'pop', 'imap',
            'cdn', 'static', 'assets', 'media', 'images', 'img', 'upload', 'uploads',
            'download', 'downloads', 'files', 'file', 'share', 'cloud', 'backup',
            'm', 'mobile', 'wap', 'secure', 'ssl', 'vpn', 'remote', 'access',
            'intranet', 'internal', 'private', 'public', 'external', 'guest'
        ]
        
        discovered = set()
        
        for subdomain in common_subdomains:
            full_domain = f"{subdomain}.{domain}"
            
            try:
                # Quick DNS lookup
                result = subprocess.run([
                    'dig', 'A', full_domain, '+short'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Verify it's not a wildcard response
                    if not self._is_wildcard_response(domain, result.stdout.strip()):
                        discovered.add(full_domain)
                        print(f"{Colors.GREEN}   ✅ Found: {full_domain}{Colors.END}")
                
            except Exception:
                continue
        
        if discovered:
            print(f"{Colors.GREEN}   🎯 Brute force found {len(discovered)} subdomains{Colors.END}")
        else:
            print(f"{Colors.YELLOW}   ℹ️  No subdomains found via brute force{Colors.END}")
        
        return discovered
    
    def _detect_wildcards(self, domain: str) -> Dict:
        """Detect if domain has wildcard DNS responses"""
        print(f"{Colors.YELLOW}🃏 Detecting wildcard DNS for {domain}...{Colors.END}")
        
        # Test with random subdomains
        test_subdomains = [
            'thisisarandomsubdomainthatdoesnotexist123',
            'nonexistentsubdomain456',
            'randomtest789'
        ]
        
        wildcard_ips = set()
        
        for test_sub in test_subdomains:
            test_domain = f"{test_sub}.{domain}"
            
            try:
                result = subprocess.run([
                    'dig', 'A', test_domain, '+short'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and result.stdout.strip():
                    ips = result.stdout.strip().split('\n')
                    wildcard_ips.update(ips)
            except Exception:
                continue
        
        if wildcard_ips:
            print(f"{Colors.YELLOW}   ⚠️  Wildcard DNS detected! IPs: {list(wildcard_ips)}{Colors.END}")
            print(f"{Colors.CYAN}   💡 Subdomain brute force may be less reliable{Colors.END}")
            return {'has_wildcard': True, 'wildcard_ips': list(wildcard_ips)}
        else:
            print(f"{Colors.GREEN}   ✅ No wildcard DNS detected{Colors.END}")
            return {'has_wildcard': False, 'wildcard_ips': []}
    
    def _is_wildcard_response(self, domain: str, response_ip: str) -> bool:
        """Check if a response IP is a wildcard response"""
        # This is a simplified check - in reality you'd want to cache wildcard IPs
        # and compare against them
        return False
    
    def _reverse_dns_lookup(self, ip: str) -> Dict:
        """Perform reverse DNS lookup on IP"""
        print(f"{Colors.YELLOW}🔄 Reverse DNS lookup for {ip}...{Colors.END}")
        
        try:
            result = subprocess.run([
                'dig', '-x', ip, '+short'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                ptr_records = result.stdout.strip().split('\n')
                ptr_records = [ptr.rstrip('.') for ptr in ptr_records if ptr.strip()]
                
                if ptr_records:
                    print(f"{Colors.GREEN}   ✅ PTR records: {ptr_records}{Colors.END}")
                    return {'success': True, 'ptr_records': ptr_records}
            
            print(f"{Colors.YELLOW}   ℹ️  No PTR records found{Colors.END}")
            return {'success': False, 'ptr_records': []}
            
        except Exception as e:
            print(f"{Colors.YELLOW}   ⚠️  Reverse DNS failed: {str(e)}{Colors.END}")
            return {'success': False, 'error': str(e)}
    
    def _save_dns_results(self, results: Dict, run_command_func) -> None:
        """Save DNS enumeration results to file"""
        try:
            import json
            
            # Create a readable summary
            summary = [
                "DNS Enumeration Results",
                "=" * 50,
                ""
            ]
            
            # Zone Transfer Results
            if results['zone_transfers']:
                summary.append("ZONE TRANSFER RESULTS:")
                summary.append("-" * 25)
                for domain, zt_result in results['zone_transfers'].items():
                    if zt_result['success']:
                        summary.append(f"✅ {domain}: {zt_result['count']} subdomains from zone transfer")
                        for subdomain in zt_result['subdomains']:
                            summary.append(f"   - {subdomain}")
                    else:
                        summary.append(f"❌ {domain}: {zt_result['reason']}")
                summary.append("")
            
            # Discovered Subdomains
            if results['subdomains']:
                summary.append("DISCOVERED SUBDOMAINS:")
                summary.append("-" * 25)
                for subdomain in sorted(results['subdomains']):
                    summary.append(f"   - {subdomain}")
                summary.append("")
            
            # DNS Records
            if results['dns_records']:
                summary.append("DNS RECORDS:")
                summary.append("-" * 15)
                for domain, records in results['dns_records'].items():
                    summary.append(f"{domain}:")
                    for record_type, values in records.items():
                        summary.append(f"   {record_type}: {', '.join(values)}")
                summary.append("")
            
            # Wildcard Detection
            if results['wildcards']:
                summary.append("WILDCARD DETECTION:")
                summary.append("-" * 20)
                for domain, wildcard_info in results['wildcards'].items():
                    if wildcard_info['has_wildcard']:
                        summary.append(f"⚠️  {domain}: Wildcard DNS detected ({wildcard_info['wildcard_ips']})")
                    else:
                        summary.append(f"✅ {domain}: No wildcard DNS")
                summary.append("")
            
            # Raw JSON data
            summary.append("RAW DATA (JSON):")
            summary.append("-" * 18)
            summary.append(json.dumps(results, indent=2, default=str))
            
            # Write to file
            with open('dns_enumeration.txt', 'w') as f:
                f.write('\n'.join(summary))
            
            print(f"{Colors.GREEN}📄 DNS enumeration results saved to dns_enumeration.txt{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not save DNS results: {str(e)}{Colors.END}")

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
    
    def theharvester_domain_scan(self, domain: str, run_command_func) -> Dict:
        """Run theHarvester against a specific domain"""
        print(f"{Colors.GREEN}🌐 Running theHarvester against domain: {domain}{Colors.END}")
        
        harvester_config = self.config['theharvester']
        
        command = [
            'theHarvester',
            '-d', domain,
            '-b', harvester_config['data_source'],
            '-l', str(harvester_config['limit'])
        ]
        
        return run_command_func(command, f'theharvester_{domain.replace(".", "_")}.txt', 
                              f'theHarvester Domain Scan ({domain})', 'theharvester') 