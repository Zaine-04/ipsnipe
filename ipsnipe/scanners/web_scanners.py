#!/usr/bin/env python3
"""
Web scanner implementations for ipsnipe
Handles feroxbuster, ffuf, and whatweb scanning
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
        self.primary_domain = None
        self.wordlist_manager = None
    
    def should_run_web_scan(self, scan_type: str, web_ports: List[int]) -> bool:
        """Determine if web scan should run based on available web ports"""
        if not web_ports:
            print(f"{Colors.YELLOW}⏭️  Skipping {scan_type} - No web services detected{Colors.END}")
            print(f"{Colors.CYAN}💡 Common web ports (80, 443) may not have been identified as web services{Colors.END}")
            print(f"{Colors.CYAN}💡 Try running whatweb manually if you suspect web services{Colors.END}")
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
                    '--user-agent', 'ipsnipe/2.1',
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
    
    def set_primary_domain(self, domain: str):
        """Set the primary domain to use for web scanning"""
        self.primary_domain = domain
        print(f"{Colors.CYAN}🔧 Web scanners will use domain: {domain}{Colors.END}")
    
    def set_wordlist_manager(self, wordlist_manager):
        """Set the wordlist manager for dynamic wordlist selection"""
        self.wordlist_manager = wordlist_manager
    
    def get_best_web_port(self, target_ip: str, web_ports: List[int]) -> tuple:
        """Get the best responsive web port and URL"""
        if not web_ports:
            return None, None
        
        # Use domain name if available
        scan_target = self.primary_domain if self.primary_domain else target_ip
        
        # Test responsiveness of web ports
        responsive_ports = []
        
        print(f"{Colors.YELLOW}🔍 Testing web port responsiveness on {scan_target}...{Colors.END}")
        
        for port in web_ports[:5]:  # Test up to 5 ports to avoid delays
            result = self.test_web_port_responsiveness(scan_target, port)
            if result['responsive']:
                responsive_ports.append(result)
                print(f"{Colors.GREEN}✅ {result['url']} - {result['status_code']} ({result['server']}){Colors.END}")
        
        if not responsive_ports:
            print(f"{Colors.YELLOW}⚠️  No responsive web services found on tested ports{Colors.END}")
            # Return the first web port with HTTP as fallback
            protocol = 'https' if web_ports[0] in [443, 8443] else 'http'
            fallback_url = f"{protocol}://{scan_target}:{web_ports[0]}"
            return web_ports[0], fallback_url
        
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
        
        if self.primary_domain:
            print(f"{Colors.GREEN}🎯 Selected target: {best_port_info['url']} (using domain){Colors.END}")
        else:
            print(f"{Colors.GREEN}🎯 Selected target: {best_port_info['url']}{Colors.END}")
        
        return port, best_port_info['url']
    
    def get_wordlist_path(self, wordlist_type: str) -> str:
        """Get the path to a wordlist file with better fallback handling"""
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
        
        # Try to use wordlist manager for fallback
        if self.wordlist_manager:
            try:
                _, fallback_path = self.wordlist_manager._get_default_wordlist()
                if fallback_path:
                    print(f"{Colors.YELLOW}⚠️  Using wordlist manager fallback: {fallback_path}{Colors.END}")
                    return fallback_path
            except:
                pass
        
        # Create minimal wordlist as last resort
        minimal_path = self.create_minimal_wordlist()
        if minimal_path:
            print(f"{Colors.YELLOW}⚠️  Using minimal wordlist: {minimal_path}{Colors.END}")
            return minimal_path
        
        print(f"{Colors.RED}❌ No wordlists available and cannot create minimal wordlist{Colors.END}")
        return None
    
    def get_ffuf_wordlist_path(self) -> str:
        """Get the path to FFUF-specific wordlist (subdomain-focused)"""
        ffuf_config = self.config['ffuf']
        
        # Use FFUF-specific wordlist if configured
        if 'wordlist' in ffuf_config:
            wordlist_path = ffuf_config['wordlist']
            if Path(wordlist_path).exists():
                print(f"{Colors.GREEN}📋 Using FFUF subdomain wordlist: {wordlist_path}{Colors.END}")
                return wordlist_path
        
        # Fallback to subdomain-specific wordlists
        subdomain_fallback_paths = [
            '/usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt',
            '/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt',
            '/usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt',
            '/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt',
            '/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt',
            '/opt/SecLists/Discovery/DNS/bitquark-subdomains-top100000.txt'
        ]
        
        for path in subdomain_fallback_paths:
            if Path(path).exists():
                print(f"{Colors.YELLOW}⚠️  Using fallback FFUF subdomain wordlist: {path}{Colors.END}")
                return path
        
        # If no subdomain wordlists found, fall back to directory wordlists
        print(f"{Colors.YELLOW}⚠️  No subdomain wordlists found, using directory wordlist for FFUF{Colors.END}")
        return self.get_wordlist_path('common')
    
    def get_ferox_wordlist_path(self, size: str = 'small') -> str:
        """Get the path to a Feroxbuster-specific wordlist file with better fallback handling"""
        ferox_config = self.config['feroxbuster']
        
        # Use wordlist manager if available
        if self.wordlist_manager:
            try:
                _, wordlist_path = self.wordlist_manager._get_default_wordlist()
                if wordlist_path:
                    return wordlist_path
            except:
                pass
        
        # Try size-specific wordlist from config
        size_key = f'wordlist_{size}'
        if size_key in ferox_config:
            wordlist_path = ferox_config[size_key]
            if Path(wordlist_path).exists():
                return wordlist_path
        
        # Default feroxbuster wordlist
        if 'wordlist' in ferox_config:
            wordlist_path = ferox_config['wordlist']
            if Path(wordlist_path).exists():
                return wordlist_path
        
        # Fallback to general wordlist method
        return self.get_wordlist_path('common')
    
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

    def feroxbuster_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run Feroxbuster directory enumeration scan with wordlist selection"""
        if not self.should_run_web_scan('Feroxbuster', web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        ferox_config = self.config['feroxbuster']
        
        # Get wordlist using wordlist manager if available, otherwise use default
        if self.wordlist_manager:
            try:
                wordlist_type, wordlist_path = self.wordlist_manager.prompt_wordlist_selection("Feroxbuster directory enumeration")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⏭️  Skipping Feroxbuster - user cancelled wordlist selection{Colors.END}")
                return {'status': 'skipped', 'reason': 'User cancelled wordlist selection'}
            except Exception as e:
                print(f"{Colors.RED}❌ Error getting wordlist: {str(e)}{Colors.END}")
                print(f"{Colors.YELLOW}⚠️  Falling back to default wordlist method{Colors.END}")
                wordlist_path = self.get_ferox_wordlist_path('medium')
                wordlist_type = 'medium'
        else:
            # Fallback to default medium wordlist
            wordlist_path = self.get_ferox_wordlist_path('medium')
            wordlist_type = 'medium'
        
        if not wordlist_path:
            return {'status': 'failed', 'reason': 'No wordlist available - ensure wordlists are installed or running in HTB environment'}
        
        print(f"{Colors.GREEN}🦀 Running Feroxbuster directory enumeration{Colors.END}")
        print(f"{Colors.CYAN}🎯 Target: {base_url}{Colors.END}")
        print(f"{Colors.CYAN}📋 Wordlist: {wordlist_path} ({wordlist_type}){Colors.END}")
        
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
        
        return run_command_func(command, 'feroxbuster.txt', f'Feroxbuster Directory Enumeration ({wordlist_type})', 'feroxbuster')
    
    def get_multiple_ffuf_wordlists(self) -> List[str]:
        """Get multiple wordlists for comprehensive FFUF subdomain enumeration"""
        wordlists = []
        
        # Priority order: small to large subdomain wordlists
        potential_wordlists = [
            '/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt',
            '/usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt', 
            '/usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt',
            '/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt',
            '/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-20000.txt',
            '/usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt',
            '/opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt',
            '/opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt',
            '/opt/SecLists/Discovery/DNS/bitquark-subdomains-top100000.txt'
        ]
        
        for wordlist in potential_wordlists:
            if Path(wordlist).exists() and wordlist not in wordlists:
                wordlists.append(wordlist)
                if len(wordlists) >= 3:  # Use up to 3 wordlists
                    break
        
        # Fallback if no subdomain wordlists found
        if not wordlists:
            # Try to use wordlist manager for fallback
            if self.wordlist_manager:
                try:
                    _, fallback_path = self.wordlist_manager._get_default_wordlist()
                    if fallback_path:
                        wordlists.append(fallback_path)
                        print(f"{Colors.YELLOW}⚠️  No subdomain wordlists found, using fallback: {fallback_path}{Colors.END}")
                except:
                    # Create minimal subdomain wordlist as last resort
                    minimal_path = self.create_minimal_subdomain_wordlist()
                    if minimal_path:
                        wordlists.append(minimal_path)
                        print(f"{Colors.YELLOW}⚠️  Created minimal subdomain wordlist: {minimal_path}{Colors.END}")
            else:
                # Fallback to generic wordlist method
                fallback = self.get_wordlist_path('common')
                if fallback:
                    wordlists.append(fallback)
                    print(f"{Colors.YELLOW}⚠️  No subdomain wordlists found, using fallback: {fallback}{Colors.END}")
                else:
                    # Create minimal subdomain wordlist as last resort
                    minimal_path = self.create_minimal_subdomain_wordlist()
                    if minimal_path:
                        wordlists.append(minimal_path)
                        print(f"{Colors.YELLOW}⚠️  Created minimal subdomain wordlist: {minimal_path}{Colors.END}")
        
        return wordlists

    def create_minimal_subdomain_wordlist(self) -> str:
        """Create a minimal subdomain wordlist for FFUF when no others are available"""
        # Common subdomain names for HTB and general pentest scenarios
        minimal_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autopilot', 'autoconfig', 'autodiscover', 'm', 'imap',
            'test', 'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn',
            'ns3', 'mail2', 'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx',
            'static', 'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar',
            'wiki', 'web', 'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal',
            'video', 'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns4', 'www3', 'dns',
            'search', 'staging', 'server', 'mx1', 'chat', 'wap', 'my', 'svn', 'mail1',
            'sites', 'proxy', 'ads', 'host', 'crm', 'cms', 'backup', 'mx2', 'lyncdiscover',
            'info', 'apps', 'download', 'remote', 'db', 'forums', 'store', 'relay',
            'files', 'newsletter', 'app', 'live', 'owa', 'en', 'start', 'sms', 'office',
            'exchange', 'ipv4', 'mail3', 'help', 'blogs', 'helpdesk', 'web1', 'home',
            'library', 'ftp2', 'ntp', 'monitor', 'login', 'service', 'correo', 'www4',
            'moodle', 'mail4', 'payment', 'us', 'webmail2', 'mailing', 'api2', 'ab',
            'fs', 'mirror', 'imap4', 'a', 'ntp1', 'resources', 'c', 'b', 'blackboard',
            'cvs', 'guest'
        ]
        
        # Create temporary subdomain wordlist file
        try:
            import tempfile
            import os
            
            # Create a temporary file that will be cleaned up later
            fd, minimal_path = tempfile.mkstemp(suffix='_minimal_subdomains.txt', prefix='ipsnipe_')
            with os.fdopen(fd, 'w') as f:
                f.write('\n'.join(minimal_subdomains))
            
            print(f"{Colors.YELLOW}⚠️  Created minimal subdomain wordlist: {minimal_path}{Colors.END}")
            return minimal_path
        
        except Exception as e:
            print(f"{Colors.RED}❌ Error creating minimal subdomain wordlist: {str(e)}{Colors.END}")
            return None

    def ffuf_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run FFUF subdomain enumeration with multiple wordlists"""
        # Check if we have a domain name for subdomain enumeration
        if not hasattr(self, 'primary_domain') or not self.primary_domain:
            print(f"{Colors.YELLOW}⏭️  Skipping FFUF Subdomain Enumeration - No domain name available{Colors.END}")
            print(f"{Colors.CYAN}💡 FFUF subdomain enumeration requires a domain name (e.g., example.htb){Colors.END}")
            print(f"{Colors.CYAN}💡 Domain discovery must run first to identify the target domain{Colors.END}")
            return {'status': 'skipped', 'reason': 'No domain name available for subdomain enumeration'}
        
        # Extract base domain from primary domain (e.g., app.example.htb -> example.htb)
        domain_parts = self.primary_domain.split('.')
        if len(domain_parts) >= 2:
            base_domain = '.'.join(domain_parts[-2:])  # Get last two parts (example.htb)
        else:
            base_domain = self.primary_domain
        
        # Get base URL for directory fuzzing mode
        port, base_url = self.get_best_web_port(target_ip, web_ports)
        if not base_url:
            return {'status': 'failed', 'reason': 'No responsive web services found'}
        
        # Get wordlists - use wordlist manager if available for directory enumeration mode
        # For subdomain enumeration, we still use the specialized subdomain wordlists
        if self.wordlist_manager and hasattr(self.wordlist_manager, 'check_cewl_available'):
            # Check if user wants to use cewl for directory fuzzing instead of subdomain enumeration
            try:
                print(f"{Colors.CYAN}💡 FFUF can run in subdomain enumeration or directory fuzzing mode{Colors.END}")
                mode_choice = input(f"{Colors.YELLOW}Use FFUF for (1) Subdomain enumeration or (2) Directory fuzzing? (1/2, default: 1): {Colors.END}").strip()
                
                if mode_choice == '2':
                    # Switch to directory fuzzing mode with wordlist selection
                    try:
                        wordlist_type, wordlist_path = self.wordlist_manager.prompt_wordlist_selection("FFUF directory fuzzing")
                        if not wordlist_path:
                            print(f"{Colors.RED}❌ No wordlist available for directory fuzzing, falling back to subdomain enumeration{Colors.END}")
                            wordlists = self.get_multiple_ffuf_wordlists()
                            fuzzing_mode = 'subdomain'
                            target_pattern = f"http://FUZZ.{base_domain}"
                        else:
                            wordlists = [wordlist_path]
                            fuzzing_mode = 'directory'
                            target_pattern = f"{base_url}/FUZZ"
                    except Exception as e:
                        print(f"{Colors.RED}❌ Error getting wordlist for directory fuzzing: {str(e)}{Colors.END}")
                        print(f"{Colors.YELLOW}⚠️  Falling back to subdomain enumeration mode{Colors.END}")
                        wordlists = self.get_multiple_ffuf_wordlists()
                        fuzzing_mode = 'subdomain'
                        target_pattern = f"http://FUZZ.{base_domain}"
                else:
                    # Use subdomain enumeration mode with specialized wordlists
                    wordlists = self.get_multiple_ffuf_wordlists()
                    fuzzing_mode = 'subdomain'
                    target_pattern = f"http://FUZZ.{base_domain}"
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⏭️  Using default subdomain enumeration mode{Colors.END}")
                wordlists = self.get_multiple_ffuf_wordlists()
                fuzzing_mode = 'subdomain'
                target_pattern = f"http://FUZZ.{base_domain}"
        else:
            # Default to subdomain enumeration
            wordlists = self.get_multiple_ffuf_wordlists()
            fuzzing_mode = 'subdomain'
            target_pattern = f"http://FUZZ.{base_domain}"
        
        # Check if we have any valid wordlists
        if not wordlists or not any(w for w in wordlists):
            return {'status': 'failed', 'reason': 'No valid wordlists available - ensure wordlists are installed or running in HTB environment'}
        
        print(f"{Colors.GREEN}💨 Running FFUF {fuzzing_mode} enumeration with {len(wordlists)} wordlist(s){Colors.END}")
        if fuzzing_mode == 'subdomain':
            print(f"{Colors.CYAN}🎯 Target domain: {base_domain}{Colors.END}")
        else:
            print(f"{Colors.CYAN}🎯 Target URL: {base_url}{Colors.END}")
        print(f"{Colors.CYAN}📋 Wordlists: {', '.join([Path(w).name for w in wordlists if w])}{Colors.END}")
        
        ffuf_config = self.config['ffuf']
        
        # Combine all wordlists into a single comma-separated string for ffuf
        valid_wordlists = [w for w in wordlists if w]
        combined_wordlists = ','.join(valid_wordlists)
        
        command = [
            'ffuf',
            '-u', target_pattern,  # Dynamic pattern based on mode
            '-w', combined_wordlists,  # Multiple wordlists
            '-t', str(ffuf_config['threads']),
            '-timeout', str(ffuf_config['timeout']),
            '-mc', ffuf_config['match_codes'],
            '-s'  # Silent mode
        ]
        
        # Add filter size if specified
        if ffuf_config['filter_size']:
            command.extend(['-fs', ffuf_config['filter_size']])
        
        # Add wildcard detection and filtering
        command.extend(['-fw'])  # Filter by word count to handle wildcards
        
        if fuzzing_mode == 'subdomain':
            scan_description = f'FFUF Subdomain Enumeration ({len(wordlists)} wordlists on {base_domain})'
            output_prefix = 'ffuf_subdomains'
        else:
            scan_description = f'FFUF Directory Fuzzing ({len(wordlists)} wordlists)'
            output_prefix = 'ffuf_directories'
        
        # Also test HTTPS if available (for subdomain mode) or if target is HTTPS (for directory mode)
        results = []
        
        # Run HTTP enumeration
        http_result = run_command_func(command, f'{output_prefix}_http.txt', scan_description + ' - HTTP', 'ffuf')
        results.append(http_result)
        
        # Run HTTPS enumeration if applicable
        should_test_https = (
            (fuzzing_mode == 'subdomain' and (443 in web_ports or any(port in [443, 8443] for port in web_ports))) or
            (fuzzing_mode == 'directory' and target_pattern.startswith('https://'))
        )
        
        if should_test_https:
            print(f"{Colors.CYAN}🔐 Also running HTTPS {fuzzing_mode} enumeration...{Colors.END}")
            https_command = command.copy()
            if fuzzing_mode == 'subdomain':
                https_command[2] = f"https://FUZZ.{base_domain}"  # Change to HTTPS for subdomain
            else:
                https_command[2] = target_pattern.replace('http://', 'https://')  # Change to HTTPS for directory
            
            https_result = run_command_func(https_command, f'{output_prefix}_https.txt', scan_description + ' - HTTPS', 'ffuf')
            results.append(https_result)
        
        # Return combined results
        if all(r['status'] == 'success' for r in results):
            return {
                'status': 'success',
                'output_files': [r['output_file'] for r in results],
                'wordlists_used': len(wordlists),
                'protocols_tested': ['HTTP'] + (['HTTPS'] if len(results) > 1 else [])
            }
        elif any(r['status'] == 'success' for r in results):
            return {
                'status': 'partial_success',
                'output_files': [r['output_file'] for r in results if r['status'] == 'success'],
                'wordlists_used': len(wordlists),
                'protocols_tested': ['HTTP'] + (['HTTPS'] if len(results) > 1 else [])
            }
        else:
            return results[0] if results else {'status': 'failed', 'reason': 'No scans executed'}

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
            '--aggression', str(whatweb_config['aggression']),
            '--no-errors',
            base_url
        ]
        
        return run_command_func(command, 'whatweb.txt', 'WhatWeb Technology Detection', 'whatweb') 