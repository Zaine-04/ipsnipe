#!/usr/bin/env python3
"""
Enhanced Web Discovery Scanner for HTB/CTF environments
Implements advanced web content discovery techniques with optimized wordlists
"""

import subprocess
import re
import requests
import threading
import time
import json
import os
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
from ..ui.colors import Colors

class EnhancedWebScanner:
    """Enhanced web content discovery with multiple techniques"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.discovered_urls = set()
        self.discovered_files = set()
        self.technology_stack = {}
        self.robots_txt_paths = set()
        self.js_endpoints = set()
        self.sensitive_files = set()
        
        # HTB-optimized file extensions
        self.htb_extensions = [
            'php', 'html', 'htm', 'asp', 'aspx', 'jsp', 'txt', 'xml', 'json',
            'js', 'css', 'zip', 'tar', 'gz', 'bak', 'old', 'backup', 'conf',
            'config', 'cfg', 'ini', 'log', 'sql', 'db', 'sqlite', 'pdf',
            'doc', 'docx', 'xls', 'xlsx', 'csv', 'key', 'pem', 'crt', 'p12'
        ]
        
        # HTB-specific interesting paths
        self.htb_paths = [
            'admin', 'administrator', 'login', 'panel', 'dashboard', 'manage',
            'control', 'console', 'phpmyadmin', 'mysql', 'database', 'db',
            'backup', 'backups', 'config', 'configuration', 'settings',
            'upload', 'uploads', 'files', 'documents', 'docs', 'downloads',
            'api', 'api/v1', 'api/v2', 'rest', 'graphql', 'webhook',
            'test', 'testing', 'debug', 'dev', 'development', 'staging',
            'temp', 'tmp', 'cache', 'logs', 'log', 'error', 'errors',
            'flag', 'flags', 'user', 'users', 'accounts', 'profile',
            'secret', 'secrets', 'private', 'internal', 'hidden',
            'robots.txt', 'sitemap.xml', '.git', '.svn', '.htaccess',
            '.env', '.env.local', '.env.production', 'web.config'
        ]
    
    def comprehensive_discovery(self, target_ip: str, web_ports: List[int], 
                               discovered_domains: List[str], run_command_func) -> Dict:
        """Run comprehensive web discovery across all web ports and domains"""
        results = {
            'status': 'running',
            'techniques': {},
            'discovered_urls': set(),
            'discovered_files': set(),
            'interesting_findings': [],
            'tools_used': []
        }
        
        print(f"\n{Colors.CYAN}🌐 Starting Enhanced Web Discovery{Colors.END}")
        print(f"{Colors.YELLOW}📋 Target IP: {target_ip}{Colors.END}")
        print(f"{Colors.YELLOW}📋 Web Ports: {', '.join(map(str, web_ports))}{Colors.END}")
        print(f"{Colors.YELLOW}📋 Domains: {', '.join(discovered_domains) if discovered_domains else 'None'}{Colors.END}")
        
        # Build target URLs
        target_urls = []
        
        # IP-based URLs
        for port in web_ports:
            protocol = 'https' if port in [443, 8443, 9443] else 'http'
            target_urls.append(f"{protocol}://{target_ip}:{port}")
            if port in [80, 443]:  # Add without port for standard ports
                target_urls.append(f"{protocol}://{target_ip}")
        
        # Domain-based URLs
        for domain in discovered_domains:
            for port in web_ports:
                protocol = 'https' if port in [443, 8443, 9443] else 'http'
                target_urls.append(f"{protocol}://{domain}:{port}")
                if port in [80, 443]:
                    target_urls.append(f"{protocol}://{domain}")
        
        print(f"{Colors.CYAN}🎯 Testing {len(target_urls)} target URLs{Colors.END}")
        
        for target_url in target_urls:
            print(f"\n{Colors.GREEN}🔍 Scanning: {target_url}{Colors.END}")
            
            # 1. Technology Detection Enhancement
            print(f"  🔍 Phase 1: Enhanced Technology Detection")
            tech_results = self._enhanced_technology_detection(target_url, run_command_func)
            
            # 2. Directory Discovery with Multiple Tools
            print(f"  🔍 Phase 2: Multi-Tool Directory Discovery")
            dir_results = self._multi_tool_directory_discovery(target_url, run_command_func)
            
            # 3. Sensitive File Discovery
            print(f"  🔍 Phase 3: Sensitive File Discovery")
            file_results = self._sensitive_file_discovery(target_url, run_command_func)
            
            # 4. JavaScript Analysis
            print(f"  🔍 Phase 4: JavaScript Endpoint Analysis")
            js_results = self._javascript_analysis(target_url, run_command_func)
            
            # 5. Robots.txt and Sitemap Analysis
            print(f"  🔍 Phase 5: Robots & Sitemap Analysis")
            robots_results = self._robots_sitemap_analysis(target_url)
            
            # 6. Parameter Discovery
            print(f"  🔍 Phase 6: Parameter Discovery")
            param_results = self._parameter_discovery(target_url, run_command_func)
            
            # Store results for this URL
            url_results = {
                'technology': tech_results,
                'directories': dir_results,
                'files': file_results,
                'javascript': js_results,
                'robots': robots_results,
                'parameters': param_results
            }
            
            results['techniques'][target_url] = url_results
        
        # Consolidate all discoveries
        self._consolidate_results(results)
        
        # Generate summary
        results['status'] = 'completed'
        self._print_summary(results)
        
        return results
    
    def _enhanced_technology_detection(self, target_url: str, run_command_func) -> Dict:
        """Enhanced technology detection with multiple methods"""
        results = {
            'whatweb': {},
            'headers': {},
            'fingerprint': {},
            'technologies': set()
        }
        
        try:
            # 1. WhatWeb scan
            cmd = f"whatweb {target_url} --aggression=1 --log-verbose=/dev/stdout"
            whatweb_result = run_command_func(cmd, timeout=60)
            if whatweb_result and whatweb_result.get('success'):
                results['whatweb'] = self._parse_whatweb_output(whatweb_result['output'])
                results['technologies'].update(results['whatweb'].get('technologies', []))
            
            # 2. Manual header analysis
            headers_result = self._analyze_headers(target_url)
            results['headers'] = headers_result
            results['technologies'].update(headers_result.get('technologies', []))
            
            # 3. Response fingerprinting
            fingerprint_result = self._fingerprint_response(target_url)
            results['fingerprint'] = fingerprint_result
            results['technologies'].update(fingerprint_result.get('technologies', []))
            
        except Exception as e:
            print(f"    ❌ Technology detection error: {e}")
        
        if results['technologies']:
            print(f"    ✅ Detected technologies: {', '.join(results['technologies'])}")
        
        return results
    
    def _multi_tool_directory_discovery(self, target_url: str, run_command_func) -> Dict:
        """Directory discovery using multiple tools and wordlists"""
        results = {
            'gobuster': {},
            'feroxbuster': {},
            'ffuf': {},
            'custom_htb': {},
            'directories': set(),
            'files': set()
        }
        
        # 1. Gobuster with HTB-optimized wordlist
        try:
            print(f"    🔍 Running Gobuster")
            wordlist = "/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
            if not os.path.exists(wordlist):
                wordlist = "/usr/share/wordlists/dirb/common.txt"
            
            cmd = f"gobuster dir -u {target_url} -w {wordlist} -x {','.join(self.htb_extensions[:10])} -t 50 -q --timeout=10s"
            gobuster_result = run_command_func(cmd, timeout=300)
            
            if gobuster_result and gobuster_result.get('success'):
                results['gobuster'] = self._parse_gobuster_output(gobuster_result['output'])
                results['directories'].update(results['gobuster'].get('directories', []))
                results['files'].update(results['gobuster'].get('files', []))
        except Exception as e:
            print(f"      ❌ Gobuster error: {e}")
        
        # 2. Custom HTB path testing
        try:
            print(f"    🔍 Testing HTB-specific paths")
            custom_results = self._test_htb_paths(target_url)
            results['custom_htb'] = custom_results
            results['directories'].update(custom_results.get('directories', []))
            results['files'].update(custom_results.get('files', []))
        except Exception as e:
            print(f"      ❌ HTB path testing error: {e}")
        
        print(f"    ✅ Found {len(results['directories'])} directories, {len(results['files'])} files")
        return results
    
    def _sensitive_file_discovery(self, target_url: str, run_command_func) -> Dict:
        """Discover sensitive files and backups"""
        results = {
            'sensitive_files': set(),
            'backup_files': set(),
            'config_files': set(),
            'interesting': []
        }
        
        # Common sensitive files for HTB
        sensitive_files = [
            'robots.txt', 'sitemap.xml', '.htaccess', '.htpasswd',
            'web.config', 'configuration.php', 'config.php', 'wp-config.php',
            '.env', '.env.local', '.env.production', '.env.backup',
            'database.yml', 'secrets.yml', 'application.yml',
            'backup.sql', 'dump.sql', 'database.sql', 'db.sql',
            'id_rsa', 'id_dsa', 'private.key', 'server.key',
            'flag.txt', 'user.txt', 'root.txt', 'flag',
            'README.md', 'CHANGELOG', 'VERSION', 'INSTALL',
            'phpinfo.php', 'info.php', 'test.php',
            'admin.php', 'login.php', 'panel.php',
            '.git/config', '.git/HEAD', '.git/logs/HEAD',
            '.svn/entries', '.bzr/branch-format'
        ]
        
        print(f"    🎯 Testing {len(sensitive_files)} sensitive files")
        
        for file_path in sensitive_files:
            try:
                test_url = urljoin(target_url + '/', file_path)
                response = requests.get(test_url, timeout=10, allow_redirects=False)
                
                if response.status_code == 200:
                    results['sensitive_files'].add(file_path)
                    results['interesting'].append({
                        'url': test_url,
                        'status': response.status_code,
                        'size': len(response.content),
                        'type': 'sensitive_file'
                    })
                    print(f"      ✅ Found: {file_path} (200)")
                    
                elif response.status_code in [403, 401]:
                    results['interesting'].append({
                        'url': test_url,
                        'status': response.status_code,
                        'type': 'protected_file'
                    })
                    print(f"      🔒 Protected: {file_path} ({response.status_code})")
                    
            except Exception:
                pass
        
        return results
    
    def _javascript_analysis(self, target_url: str, run_command_func) -> Dict:
        """Analyze JavaScript files for endpoints and secrets"""
        results = {
            'js_files': [],
            'endpoints': set(),
            'secrets': [],
            'api_endpoints': set()
        }
        
        try:
            # First get the main page to find JS files
            response = requests.get(target_url, timeout=10)
            if response.status_code == 200:
                # Find JavaScript files
                js_pattern = r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']'
                js_files = re.findall(js_pattern, response.text, re.IGNORECASE)
                
                for js_file in js_files:
                    js_url = urljoin(target_url, js_file)
                    results['js_files'].append(js_url)
                    
                    # Analyze each JS file
                    try:
                        js_response = requests.get(js_url, timeout=10)
                        if js_response.status_code == 200:
                            js_content = js_response.text
                            
                            # Find API endpoints
                            api_patterns = [
                                r'["\']([/][api][^"\']*)["\']',
                                r'["\']([/][a-zA-Z0-9/_-]+\.php)["\']',
                                r'["\']([/][a-zA-Z0-9/_-]+\.asp[x]?)["\']',
                                r'["\']([/][a-zA-Z0-9/_-]+\.jsp)["\']'
                            ]
                            
                            for pattern in api_patterns:
                                endpoints = re.findall(pattern, js_content)
                                results['endpoints'].update(endpoints)
                                results['api_endpoints'].update(endpoints)
                            
                            # Find potential secrets
                            secret_patterns = [
                                r'api[_-]?key["\'\s]*[:=]["\'\s]*([a-zA-Z0-9_-]{20,})',
                                r'secret[_-]?key["\'\s]*[:=]["\'\s]*([a-zA-Z0-9_-]{20,})',
                                r'password["\'\s]*[:=]["\'\s]*([a-zA-Z0-9_-]{8,})',
                                r'token["\'\s]*[:=]["\'\s]*([a-zA-Z0-9_-]{20,})'
                            ]
                            
                            for pattern in secret_patterns:
                                secrets = re.findall(pattern, js_content, re.IGNORECASE)
                                results['secrets'].extend(secrets)
                                
                    except Exception:
                        pass
                
                print(f"    ✅ Analyzed {len(js_files)} JS files, found {len(results['endpoints'])} endpoints")
                
        except Exception as e:
            print(f"    ❌ JavaScript analysis error: {e}")
        
        return results
    
    def _robots_sitemap_analysis(self, target_url: str) -> Dict:
        """Analyze robots.txt and sitemap.xml for additional paths"""
        results = {
            'robots_paths': set(),
            'sitemap_urls': set(),
            'disallowed': set(),
            'interesting': []
        }
        
        # Analyze robots.txt
        try:
            robots_url = urljoin(target_url, '/robots.txt')
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                robots_content = response.text
                
                # Extract disallowed paths
                disallow_pattern = r'Disallow:\s*([^\s]+)'
                disallowed = re.findall(disallow_pattern, robots_content)
                results['disallowed'].update(disallowed)
                results['robots_paths'].update(disallowed)
                
                # Extract sitemap URLs
                sitemap_pattern = r'Sitemap:\s*([^\s]+)'
                sitemaps = re.findall(sitemap_pattern, robots_content)
                results['sitemap_urls'].update(sitemaps)
                
                print(f"    ✅ Found {len(disallowed)} disallowed paths, {len(sitemaps)} sitemaps")
                
        except Exception:
            pass
        
        # Analyze sitemaps
        for sitemap_url in results['sitemap_urls']:
            try:
                response = requests.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    # Extract URLs from sitemap
                    url_pattern = r'<loc>([^<]+)</loc>'
                    urls = re.findall(url_pattern, response.text)
                    
                    for url in urls:
                        parsed = urlparse(url)
                        results['robots_paths'].add(parsed.path)
                        
            except Exception:
                pass
        
        return results
    
    def _parameter_discovery(self, target_url: str, run_command_func) -> Dict:
        """Discover URL parameters using various techniques"""
        results = {
            'parameters': set(),
            'endpoints_with_params': set(),
            'common_params': []
        }
        
        # Common HTB/CTF parameters
        common_params = [
            'id', 'user', 'username', 'page', 'file', 'path', 'dir',
            'debug', 'test', 'admin', 'cmd', 'exec', 'system',
            'include', 'require', 'read', 'load', 'fetch',
            'search', 'query', 'q', 'term', 'keyword',
            'filter', 'sort', 'order', 'limit', 'offset',
            'action', 'method', 'function', 'class', 'module',
            'data', 'input', 'value', 'content', 'text'
        ]
        
        # Test common parameters
        for param in common_params:
            try:
                test_url = f"{target_url}?{param}=test"
                response = requests.get(test_url, timeout=10, allow_redirects=False)
                
                # Different response might indicate parameter is recognized
                original_response = requests.get(target_url, timeout=10, allow_redirects=False)
                
                if (response.status_code != original_response.status_code or 
                    len(response.content) != len(original_response.content)):
                    results['parameters'].add(param)
                    results['common_params'].append(param)
                    
            except Exception:
                pass
        
        if results['parameters']:
            print(f"    ✅ Found {len(results['parameters'])} potential parameters")
        
        return results
    
    def _parse_whatweb_output(self, output: str) -> Dict:
        """Parse WhatWeb output for technology information"""
        results = {
            'technologies': set(),
            'versions': {},
            'raw_output': output
        }
        
        # Extract technology names and versions
        tech_patterns = [
            r'(\w+)\[([^\]]+)\]',
            r'(\w+)-([0-9.]+)',
            r'(Apache|Nginx|IIS|PHP|MySQL|PostgreSQL|WordPress|Drupal|Joomla)'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    tech = match[0]
                    if len(match) > 1:
                        version = match[1]
                        results['versions'][tech] = version
                else:
                    tech = match
                results['technologies'].add(tech)
        
        return results
    
    def _analyze_headers(self, target_url: str) -> Dict:
        """Analyze HTTP headers for technology information"""
        results = {
            'technologies': set(),
            'headers': {},
            'security_headers': {}
        }
        
        try:
            response = requests.head(target_url, timeout=10)
            results['headers'] = dict(response.headers)
            
            # Extract technology information from headers
            tech_headers = {
                'Server': r'(Apache|Nginx|IIS|lighttpd|Tomcat)',
                'X-Powered-By': r'(PHP|ASP\.NET|Express)',
                'X-Generator': r'(WordPress|Drupal|Joomla)',
                'X-AspNet-Version': r'([0-9.]+)',
            }
            
            for header, pattern in tech_headers.items():
                if header in results['headers']:
                    matches = re.findall(pattern, results['headers'][header], re.IGNORECASE)
                    results['technologies'].update(matches)
            
            # Security headers
            security_headers = [
                'X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options',
                'Strict-Transport-Security', 'Content-Security-Policy'
            ]
            
            for header in security_headers:
                if header in results['headers']:
                    results['security_headers'][header] = results['headers'][header]
                    
        except Exception:
            pass
        
        return results
    
    def _fingerprint_response(self, target_url: str) -> Dict:
        """Fingerprint the web application response"""
        results = {
            'technologies': set(),
            'characteristics': {},
            'error_pages': {}
        }
        
        try:
            # Test various paths to fingerprint the application
            test_paths = [
                '/',
                '/nonexistent-page-12345',
                '/admin',
                '/test.php',
                '/test.asp'
            ]
            
            for path in test_paths:
                test_url = urljoin(target_url, path)
                response = requests.get(test_url, timeout=10, allow_redirects=False)
                
                # Analyze response characteristics
                if 'php' in response.text.lower() or 'X-Powered-By' in response.headers:
                    results['technologies'].add('PHP')
                
                if 'asp.net' in response.text.lower():
                    results['technologies'].add('ASP.NET')
                
                if 'wordpress' in response.text.lower():
                    results['technologies'].add('WordPress')
                
                # Store error page characteristics
                if response.status_code in [404, 403, 500]:
                    results['error_pages'][response.status_code] = {
                        'size': len(response.content),
                        'title': self._extract_title(response.text)
                    }
                    
        except Exception:
            pass
        
        return results
    
    def _parse_gobuster_output(self, output: str) -> Dict:
        """Parse Gobuster output"""
        results = {
            'directories': set(),
            'files': set(),
            'status_codes': {}
        }
        
        lines = output.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('='):
                # Parse gobuster output format
                parts = line.split()
                if len(parts) >= 2:
                    path = parts[0]
                    status = parts[1].strip('()')
                    
                    if path.endswith('/'):
                        results['directories'].add(path)
                    else:
                        results['files'].add(path)
                    
                    results['status_codes'][path] = status
        
        return results
    
    def _test_htb_paths(self, target_url: str) -> Dict:
        """Test HTB-specific paths"""
        results = {
            'directories': set(),
            'files': set(),
            'interesting': []
        }
        
        print(f"    🎯 Testing {len(self.htb_paths)} HTB-specific paths")
        
        for path in self.htb_paths:
            try:
                test_url = urljoin(target_url + '/', path)
                response = requests.get(test_url, timeout=10, allow_redirects=False)
                
                if response.status_code == 200:
                    if path.endswith('/') or '.' not in path:
                        results['directories'].add(path)
                    else:
                        results['files'].add(path)
                    
                    results['interesting'].append({
                        'path': path,
                        'url': test_url,
                        'status': response.status_code,
                        'size': len(response.content)
                    })
                    
                elif response.status_code in [301, 302, 403]:
                    results['interesting'].append({
                        'path': path,
                        'url': test_url,
                        'status': response.status_code,
                        'note': 'Redirect or Forbidden'
                    })
                    
            except Exception:
                pass
        
        return results
    
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML content"""
        match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE)
        return match.group(1) if match else ''
    
    def _consolidate_results(self, results: Dict):
        """Consolidate results from all techniques"""
        all_urls = set()
        all_files = set()
        all_interesting = []
        
        for url_results in results['techniques'].values():
            for technique_results in url_results.values():
                if 'directories' in technique_results:
                    all_urls.update(technique_results['directories'])
                if 'files' in technique_results:
                    all_files.update(technique_results['files'])
                if 'interesting' in technique_results:
                    all_interesting.extend(technique_results['interesting'])
        
        results['discovered_urls'] = all_urls
        results['discovered_files'] = all_files
        results['interesting_findings'] = all_interesting
    
    def _print_summary(self, results: Dict):
        """Print comprehensive summary of discoveries"""
        print(f"\n{Colors.GREEN}✅ Enhanced Web Discovery Complete{Colors.END}")
        print(f"{Colors.CYAN}📊 Discovery Summary:{Colors.END}")
        print(f"   • URLs discovered: {len(results['discovered_urls'])}")
        print(f"   • Files found: {len(results['discovered_files'])}")
        print(f"   • Interesting findings: {len(results['interesting_findings'])}")
        
        if results['discovered_urls']:
            print(f"\n{Colors.YELLOW}📁 Discovered directories:{Colors.END}")
            for url in sorted(list(results['discovered_urls'])[:20]):  # Show first 20
                print(f"   • {url}")
            if len(results['discovered_urls']) > 20:
                print(f"   ... and {len(results['discovered_urls']) - 20} more")
        
        if results['discovered_files']:
            print(f"\n{Colors.YELLOW}📄 Discovered files:{Colors.END}")
            for file in sorted(list(results['discovered_files'])[:20]):  # Show first 20
                print(f"   • {file}")
            if len(results['discovered_files']) > 20:
                print(f"   ... and {len(results['discovered_files']) - 20} more")
        
        if results['interesting_findings']:
            print(f"\n{Colors.YELLOW}🎯 Interesting findings:{Colors.END}")
            for finding in results['interesting_findings'][:10]:  # Show first 10
                if isinstance(finding, dict):
                    print(f"   • {finding.get('url', finding.get('path', 'Unknown'))} "
                          f"({finding.get('status', 'N/A')})") 