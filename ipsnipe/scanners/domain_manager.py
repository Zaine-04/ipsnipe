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
    
    def __init__(self, target_ip: str, use_sudo: bool = False):
        self.target_ip = target_ip
        self.use_sudo = use_sudo
        self.discovered_domains = set()
        self.hosts_file = "/etc/hosts"
        self.backup_hosts = None
        self.hosts_entries_added = []
        
        # Test sudo availability if use_sudo is enabled
        if self.use_sudo:
            self._check_sudo_availability()
    
    def _check_sudo_availability(self):
        """Check if sudo is available and working"""
        try:
            # Test sudo access with a simple command
            result = subprocess.run([
                'sudo', '-n', 'echo', 'test'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                print(f"{Colors.YELLOW}⚠️  Sudo access may require password prompt for hosts file operations{Colors.END}")
                print(f"{Colors.CYAN}💡 Consider running ipsnipe with: sudo python ipsnipe.py{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not verify sudo access: {str(e)}{Colors.END}")
    
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
                        print(f"{Colors.CYAN}   📄 HTTP Headers received for {url}{Colors.END}")
                        
                        # Look for domains in headers - enhanced patterns
                        header_patterns = [
                            r'Location:\s*https?://([a-zA-Z0-9.-]+)(?:/.*)?',  # Enhanced Location pattern
                            r'Location:\s*([a-zA-Z0-9.-]+\.(?:htb|thm|local|box))(?:/.*)?',  # HTB-specific in Location
                            r'Server:\s*([a-zA-Z0-9.-]+)',
                            r'Host:\s*([a-zA-Z0-9.-]+)',
                        ]
                        
                        for pattern in header_patterns:
                            matches = re.findall(pattern, headers, re.IGNORECASE)
                            for match in matches:
                                # More permissive domain validation
                                if (not re.match(r'^\d+\.\d+\.\d+\.\d+$', match) and 
                                    '.' in match and 
                                    len(match) > 3 and
                                    not match.endswith(('.com', '.org', '.net', '.gov', '.edu'))):
                                    domains.add(match.lower())
                                    print(f"{Colors.GREEN}   🎯 Found domain in headers: {match.lower()}{Colors.END}")
                        
                        # Debug: Show what headers we got
                        if any(word in headers.lower() for word in ['location', 'host', 'server']):
                            print(f"{Colors.CYAN}   🔍 Relevant headers found:{Colors.END}")
                            for line in headers.split('\n'):
                                if any(word in line.lower() for word in ['location', 'host', 'server']):
                                    print(f"      {line.strip()}")
                    else:
                        print(f"{Colors.YELLOW}   ⚠️  No HTTP headers received from {url}{Colors.END}")
                
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
            print(f"{Colors.CYAN}💡 Only actual discovered domains will be added to hosts file{Colors.END}")
        
        self.discovered_domains.update(valid_domains)
        return valid_domains
    
    def discover_domains_with_whatweb(self, target_ip: str, web_ports: List[int]) -> List[str]:
        """Use whatweb to discover domains from HTTP headers and redirects"""
        print(f"{Colors.YELLOW}🔍 Using whatweb to discover domains from HTTP headers...{Colors.END}")
        
        discovered_domains = set()
        
        for port in web_ports:
            # Determine protocol
            protocol = 'https' if port in [443, 8443] else 'http'
            url = f"{protocol}://{target_ip}:{port}"
            
            print(f"{Colors.CYAN}   Analyzing {url} with whatweb...{Colors.END}")
            
            try:
                # Run whatweb with verbose output to get headers
                command = [
                    'whatweb',
                    '--log-verbose=-',  # Verbose output to stdout
                    '--aggression=3',   # More aggressive for better header detection
                    '--no-errors',
                    '--max-redirects=5',  # Follow redirects to catch domain changes
                    url
                ]
                
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout:
                    output = result.stdout
                    
                    # Parse whatweb output for domains - HTB optimized patterns
                    domain_patterns = [
                        # HTB/CTF specific patterns (highest priority)
                        r'RedirectLocation\[([a-zA-Z0-9.-]+\.htb)[/\]]',
                        r'Location:\s*https?://([a-zA-Z0-9.-]+\.htb)',
                        r'Host:\s*([a-zA-Z0-9.-]+\.htb)',
                        r'Title\[.*?([a-zA-Z0-9-]+\.htb).*?\]',
                        
                        # Other CTF platforms
                        r'RedirectLocation\[([a-zA-Z0-9.-]+\.(?:thm|local|box))[/\]]',
                        r'Location:\s*https?://([a-zA-Z0-9.-]+\.(?:thm|local|box))',
                        r'Host:\s*([a-zA-Z0-9.-]+\.(?:thm|local|box))',
                        r'Title\[.*?([a-zA-Z0-9-]+\.(?:thm|local|box)).*?\]',
                        
                        # Generic redirect patterns (lower priority)
                        r'RedirectLocation\[https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[/\]]',
                        r'Location:\s*https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                        
                        # Server and host patterns
                        r'Host:\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                        r'Server:\s*([a-zA-Z0-9.-]+\.(?:htb|thm|local|box))',
                        
                        # Content-based patterns for HTB
                        r'content["\'].*?([a-zA-Z0-9-]+\.htb)',
                        r'href["\'].*?([a-zA-Z0-9-]+\.htb)',
                        r'src["\'].*?([a-zA-Z0-9-]+\.htb)',
                    ]
                    
                    for pattern in domain_patterns:
                        matches = re.findall(pattern, output, re.IGNORECASE)
                        for match in matches:
                            # Validate domain
                            if (not re.match(r'^\d+\.\d+\.\d+\.\d+$', match) and 
                                '.' in match and 
                                len(match) > 3 and
                                not match.endswith(('.com', '.org', '.net', '.gov', '.edu', '.io'))):
                                discovered_domains.add(match.lower())
                                print(f"{Colors.GREEN}   🎯 Found domain in whatweb output: {match.lower()}{Colors.END}")
                    
                    # Debug: Show relevant parts of whatweb output
                    if any(keyword in output.lower() for keyword in ['location', 'redirect', 'host', '.htb', '.thm', '.local', '.box']):
                        print(f"{Colors.CYAN}   📄 Relevant whatweb output:{Colors.END}")
                        for line in output.split('\n'):
                            if any(keyword in line.lower() for keyword in ['location', 'redirect', 'host', '.htb', '.thm', '.local', '.box']):
                                print(f"      {line.strip()}")
                
                else:
                    print(f"{Colors.YELLOW}   ⚠️  Whatweb scan failed for {url}{Colors.END}")
                    
            except Exception as e:
                print(f"{Colors.YELLOW}   ⚠️  Error running whatweb on {url}: {str(e)}{Colors.END}")
        
        valid_domains = list(discovered_domains)
        
        if valid_domains:
            print(f"{Colors.GREEN}🌐 Whatweb discovered domains: {valid_domains}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  No domains discovered by whatweb{Colors.END}")
        
        self.discovered_domains.update(valid_domains)
        return valid_domains

    
    def backup_hosts_file(self) -> bool:
        """Create a backup of the current /etc/hosts file"""
        try:
            if os.path.exists(self.hosts_file):
                backup_path = f"{self.hosts_file}.ipsnipe.backup"
                
                if self.use_sudo:
                    # Use sudo for backup operation
                    result = subprocess.run([
                        'sudo', 'cp', self.hosts_file, backup_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.backup_hosts = backup_path
                        print(f"{Colors.GREEN}✅ Created hosts file backup: {backup_path}{Colors.END}")
                        return True
                    else:
                        print(f"{Colors.RED}❌ Failed to backup hosts file: {result.stderr}{Colors.END}")
                        return False
                else:
                    # Try without sudo first
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
            
            if self.use_sudo:
                # Use sudo to modify hosts file
                return self._add_entries_with_sudo(new_entries, ipsnipe_marker, current_content)
            else:
                # Try direct modification first
                return self._add_entries_direct(new_entries, ipsnipe_marker, current_content)
            
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to update hosts file: {str(e)}{Colors.END}")
            return False
    
    def _add_entries_with_sudo(self, new_entries: List[str], marker: str, current_content: str) -> bool:
        """Add entries to hosts file using sudo"""
        try:
            # Create temporary file with new content
            temp_file = f"/tmp/ipsnipe_hosts_{os.getpid()}"
            
            with open(temp_file, 'w') as f:
                f.write(current_content)
                if marker not in current_content:
                    f.write(f"\n{marker}\n")
                for entry in new_entries:
                    f.write(f"{entry}\n")
            
            # Use sudo to copy temp file to hosts file
            result = subprocess.run([
                'sudo', 'cp', temp_file, self.hosts_file
            ], capture_output=True, text=True)
            
            # Clean up temp file
            os.remove(temp_file)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Added {len(new_entries)} domain(s) to /etc/hosts:{Colors.END}")
                for entry in new_entries:
                    print(f"   {Colors.CYAN}{entry}{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Failed to update hosts file with sudo: {result.stderr}{Colors.END}")
                self._show_manual_instructions(new_entries)
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Error using sudo to update hosts file: {str(e)}{Colors.END}")
            self._show_manual_instructions(new_entries)
            return False
    
    def _add_entries_direct(self, new_entries: List[str], marker: str, current_content: str) -> bool:
        """Add entries to hosts file directly (without sudo)"""
        try:
            # Add entries to hosts file
            with open(self.hosts_file, 'a') as f:
                if marker not in current_content:
                    f.write(f"\n{marker}\n")
                for entry in new_entries:
                    f.write(f"{entry}\n")
            
            print(f"{Colors.GREEN}✅ Added {len(new_entries)} domain(s) to /etc/hosts:{Colors.END}")
            for entry in new_entries:
                print(f"   {Colors.CYAN}{entry}{Colors.END}")
            
            return True
            
        except PermissionError:
            print(f"{Colors.RED}❌ Permission denied accessing /etc/hosts{Colors.END}")
            print(f"{Colors.YELLOW}💡 This usually happens when ipsnipe is not run with sudo{Colors.END}")
            self._show_manual_instructions(new_entries)
            return False
    
    def _show_manual_instructions(self, entries: List[str]):
        """Show manual instructions for adding hosts entries"""
        print(f"{Colors.YELLOW}📝 Manual hosts file update required:{Colors.END}")
        print(f"{Colors.CYAN}   sudo nano /etc/hosts{Colors.END}")
        print(f"{Colors.YELLOW}   Add these lines:{Colors.END}")
        for entry in entries:
            print(f"   {Colors.CYAN}{entry}{Colors.END}")
    
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
                
                if self.use_sudo:
                    self._cleanup_with_sudo()
                else:
                    self._cleanup_direct()
                
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not clean up hosts file: {str(e)}{Colors.END}")
            if self.backup_hosts:
                restore_cmd = f"sudo cp {self.backup_hosts} {self.hosts_file}" if self.use_sudo else f"cp {self.backup_hosts} {self.hosts_file}"
                print(f"{Colors.CYAN}💡 Restore from backup: {restore_cmd}{Colors.END}")
    
    def _cleanup_with_sudo(self):
        """Clean up hosts file using sudo"""
        try:
            # Read current hosts file
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
            
            # Write to temp file
            temp_file = f"/tmp/ipsnipe_hosts_cleanup_{os.getpid()}"
            with open(temp_file, 'w') as f:
                f.writelines(filtered_lines)
            
            # Use sudo to copy temp file to hosts file
            result = subprocess.run([
                'sudo', 'cp', temp_file, self.hosts_file
            ], capture_output=True, text=True)
            
            # Clean up temp file
            os.remove(temp_file)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Cleaned up hosts file{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Could not clean up hosts file: {result.stderr}{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Error during sudo cleanup: {str(e)}{Colors.END}")
    
    def _cleanup_direct(self):
        """Clean up hosts file directly"""
        try:
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
            
        except PermissionError:
            print(f"{Colors.YELLOW}⚠️  Permission denied cleaning up hosts file{Colors.END}")
            print(f"{Colors.CYAN}💡 Manual cleanup: sudo nano /etc/hosts (remove ipsnipe entries){Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Error during cleanup: {str(e)}{Colors.END}")
    
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