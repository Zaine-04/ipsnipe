#!/usr/bin/env python3
"""
Domain management for ipsnipe
Handles /etc/hosts manipulation and domain discovery for better enumeration
"""

import os
import re
import subprocess
import tempfile
import shutil
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from ..ui.colors import Colors


class DomainManager:
    """Manages domain discovery and /etc/hosts manipulation"""
    
    def __init__(self, target_ip: str):
        self.target_ip = target_ip
        self.discovered_domains = set()
        self.hosts_file = "/etc/hosts"
        self.backup_hosts = None
        self.hosts_entries_added = []
    
    def discover_domains_from_http(self, web_services: List[Dict]) -> List[str]:
        """Discover domain names from HTTP responses and headers"""
        print(f"{Colors.YELLOW}🔍 Discovering domain names from web services...{Colors.END}")
        
        domains = set()
        
        for service in web_services:
            url = service['url']
            print(f"{Colors.CYAN}   Checking {url} for domain names...{Colors.END}")
            
            try:
                # Get full HTTP response including body
                result = subprocess.run([
                    'curl', '-s', '-L', '--max-time', '10', '--connect-timeout', '5',
                    '-k', '--user-agent', 'ipsnipe/1.0.6 (HTB Scanner)',
                    '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    url
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    # Look for domains in various places
                    content = result.stdout
                    
                    # 1. Look for common HTB/CTF patterns
                    htb_patterns = [
                        r'([a-zA-Z0-9-]+\.htb)',  # *.htb domains
                        r'([a-zA-Z0-9-]+\.thm)',  # TryHackMe domains
                        r'([a-zA-Z0-9-]+\.local)', # .local domains
                        r'([a-zA-Z0-9-]+\.box)',   # .box domains
                    ]
                    
                    for pattern in htb_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            domains.add(match.lower())
                    
                    # 2. Look for domains in HTML content
                    html_patterns = [
                        r'href=["\']https?://([a-zA-Z0-9.-]+)["\']',
                        r'src=["\']https?://([a-zA-Z0-9.-]+)["\']',
                        r'action=["\']https?://([a-zA-Z0-9.-]+)["\']',
                        r'<title>.*?([a-zA-Z0-9-]+\.(?:htb|thm|local|box)).*?</title>',
                    ]
                    
                    for pattern in html_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # Filter out IP addresses and common domains
                            if not re.match(r'\d+\.\d+\.\d+\.\d+', match) and \
                               not match.endswith(('.com', '.org', '.net', '.gov', '.edu')):
                                domains.add(match.lower())
                    
                    # 3. Get HTTP headers for more clues
                    header_result = subprocess.run([
                        'curl', '-s', '-I', '--max-time', '5', '--connect-timeout', '3',
                        '-k', url
                    ], capture_output=True, text=True, timeout=8)
                    
                    if header_result.returncode == 0:
                        headers = header_result.stdout
                        
                        # Look for domains in headers
                        header_patterns = [
                            r'Location:\s*https?://([a-zA-Z0-9.-]+)',
                            r'Server:\s*([a-zA-Z0-9.-]+)',
                            r'Host:\s*([a-zA-Z0-9.-]+)',
                        ]
                        
                        for pattern in header_patterns:
                            matches = re.findall(pattern, headers, re.IGNORECASE)
                            for match in matches:
                                if not re.match(r'\d+\.\d+\.\d+\.\d+', match) and \
                                   '.' in match and len(match) > 3:
                                    domains.add(match.lower())
                
            except Exception as e:
                print(f"{Colors.YELLOW}   ⚠️  Could not analyze {url}: {str(e)}{Colors.END}")
        
        # Filter and validate domains
        valid_domains = []
        for domain in domains:
            # Basic validation
            if (len(domain) > 3 and 
                '.' in domain and 
                not domain.startswith('.') and 
                not domain.endswith('.') and
                not re.match(r'^\d+\.\d+\.\d+\.\d+$', domain)):
                valid_domains.append(domain)
        
        if valid_domains:
            print(f"{Colors.GREEN}🌐 Discovered domains: {valid_domains}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  No domains discovered from HTTP responses{Colors.END}")
            # Try common HTB domain patterns
            common_htb_domains = self._guess_htb_domains()
            if common_htb_domains:
                print(f"{Colors.CYAN}💡 Trying common HTB domain patterns: {common_htb_domains}{Colors.END}")
                valid_domains.extend(common_htb_domains)
        
        self.discovered_domains.update(valid_domains)
        return valid_domains
    
    def _guess_htb_domains(self) -> List[str]:
        """Guess common HTB domain patterns"""
        # Get the last octet of IP for machine name guessing
        octets = self.target_ip.split('.')
        if len(octets) == 4:
            last_octet = octets[-1]
            
            # Common HTB patterns
            guesses = [
                f"machine{last_octet}.htb",
                f"box{last_octet}.htb", 
                f"target.htb",
                f"machine.htb",
                f"www.machine.htb",
            ]
            
            return guesses
        return []
    
    def backup_hosts_file(self) -> bool:
        """Create a backup of the current /etc/hosts file"""
        try:
            if os.path.exists(self.hosts_file):
                backup_path = f"{self.hosts_file}.ipsnipe.backup"
                shutil.copy2(self.hosts_file, backup_path)
                self.backup_hosts = backup_path
                print(f"{Colors.GREEN}✅ Created hosts file backup: {backup_path}{Colors.END}")
                return True
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to backup hosts file: {str(e)}{Colors.END}")
        return False
    
    def add_domains_to_hosts(self, domains: List[str]) -> bool:
        """Add discovered domains to /etc/hosts file"""
        if not domains:
            return False
        
        print(f"{Colors.YELLOW}🔧 Adding domains to /etc/hosts...{Colors.END}")
        
        try:
            # Read current hosts file
            with open(self.hosts_file, 'r') as f:
                current_content = f.read()
            
            # Prepare new entries
            new_entries = []
            ipsnipe_marker = "# ipsnipe entries"
            
            for domain in domains:
                entry = f"{self.target_ip}\t{domain}"
                if entry not in current_content:
                    new_entries.append(entry)
                    self.hosts_entries_added.append(entry)
            
            if not new_entries:
                print(f"{Colors.YELLOW}ℹ️  All domains already in hosts file{Colors.END}")
                return True
            
            # Add entries to hosts file
            with open(self.hosts_file, 'a') as f:
                if ipsnipe_marker not in current_content:
                    f.write(f"\n{ipsnipe_marker}\n")
                for entry in new_entries:
                    f.write(f"{entry}\n")
            
            print(f"{Colors.GREEN}✅ Added {len(new_entries)} domain(s) to /etc/hosts:{Colors.END}")
            for entry in new_entries:
                print(f"   {Colors.CYAN}{entry}{Colors.END}")
            
            return True
            
        except PermissionError:
            print(f"{Colors.RED}❌ Permission denied. Run with sudo to modify /etc/hosts{Colors.END}")
            print(f"{Colors.YELLOW}💡 Manually add these entries to /etc/hosts:{Colors.END}")
            for domain in domains:
                print(f"   {Colors.CYAN}{self.target_ip}\t{domain}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to update hosts file: {str(e)}{Colors.END}")
            return False
    
    def verify_domain_resolution(self, domains: List[str]) -> List[str]:
        """Verify that domains resolve to the target IP"""
        print(f"{Colors.YELLOW}🔍 Verifying domain resolution...{Colors.END}")
        
        working_domains = []
        
        for domain in domains:
            try:
                # Use nslookup or dig to verify resolution
                result = subprocess.run([
                    'nslookup', domain
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and self.target_ip in result.stdout:
                    working_domains.append(domain)
                    print(f"{Colors.GREEN}   ✅ {domain} resolves to {self.target_ip}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}   ⚠️  {domain} resolution unclear{Colors.END}")
                    # Still add it as it might work
                    working_domains.append(domain)
                    
            except Exception:
                # If nslookup fails, assume it might still work
                working_domains.append(domain)
        
        return working_domains
    
    def get_best_domain(self, domains: List[str]) -> Optional[str]:
        """Get the best domain to use for scanning"""
        if not domains:
            return None
        
        # Priority order for domain selection
        priorities = [
            lambda d: d.endswith('.htb'),      # HTB domains first
            lambda d: not d.startswith('www.'), # Non-www domains
            lambda d: len(d.split('.')) == 2,   # Simple domains
            lambda d: 'machine' in d or 'target' in d,  # Common names
        ]
        
        for priority_func in priorities:
            for domain in domains:
                if priority_func(domain):
                    return domain
        
        # Return first domain if no priority matches
        return domains[0]
    
    def cleanup_hosts_file(self):
        """Remove ipsnipe entries from hosts file"""
        try:
            if self.hosts_entries_added:
                print(f"{Colors.YELLOW}🧹 Cleaning up hosts file entries...{Colors.END}")
                
                with open(self.hosts_file, 'r') as f:
                    lines = f.readlines()
                
                # Remove ipsnipe entries
                filtered_lines = []
                skip_next = False
                
                for line in lines:
                    if "# ipsnipe entries" in line:
                        skip_next = True
                        continue
                    if skip_next and any(entry.strip() in line.strip() for entry in self.hosts_entries_added):
                        continue
                    skip_next = False
                    filtered_lines.append(line)
                
                with open(self.hosts_file, 'w') as f:
                    f.writelines(filtered_lines)
                
                print(f"{Colors.GREEN}✅ Cleaned up hosts file{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not clean up hosts file: {str(e)}{Colors.END}")
            if self.backup_hosts:
                print(f"{Colors.CYAN}💡 Restore from backup: sudo cp {self.backup_hosts} {self.hosts_file}{Colors.END}")
    
    def restore_hosts_backup(self):
        """Restore hosts file from backup"""
        try:
            if self.backup_hosts and os.path.exists(self.backup_hosts):
                shutil.copy2(self.backup_hosts, self.hosts_file)
                os.remove(self.backup_hosts)
                print(f"{Colors.GREEN}✅ Restored hosts file from backup{Colors.END}")
                return True
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to restore hosts backup: {str(e)}{Colors.END}")
        return False 