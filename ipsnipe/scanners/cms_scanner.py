#!/usr/bin/env python3
"""
CMS Detection and Enumeration Scanner for ipsnipe
Combines CMSeek and http-enum for comprehensive CMS identification
"""

import subprocess
import time
import json
from typing import Dict, List, Optional
from pathlib import Path
from ..ui.colors import Colors


class CMSScanner:
    """CMS detection and enumeration functionality"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.detected_cms = []
        self.cms_vulnerabilities = []
        self.cms_plugins = []
        self.http_enum_results = []
    
    def should_run_cms_scan(self, web_ports: List[int]) -> bool:
        """Determine if CMS scanning should run based on available web ports"""
        if not web_ports:
            print(f"{Colors.YELLOW}⏭️  Skipping CMS Detection & Enumeration - No web services detected{Colors.END}")
            print(f"{Colors.CYAN}💡 This scan requires active web services to analyze{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}🔍 Running CMS Detection & Enumeration on web ports: {web_ports}{Colors.END}")
        return True
    
    def get_web_targets(self, target_ip: str, web_ports: List[int]) -> List[str]:
        """Get all web targets for comprehensive CMS scanning"""
        targets = []
        
        for port in web_ports:
            if port in [443, 8443]:
                targets.append(f"https://{target_ip}:{port}")
            else:
                targets.append(f"http://{target_ip}:{port}")
        
        return targets
    
    def run_cmseek_scan(self, targets: List[str], run_command_func) -> Dict:
        """Run CMSeek for comprehensive CMS detection"""
        print(f"{Colors.CYAN}🔍 Step 1: Running CMSeek comprehensive CMS detection...{Colors.END}")
        
        cmseek_config = self.config.get('cmseek', {
            'threads': 10,
            'timeout': 30,
            'random_agent': True,
            'follow_redirect': True
        })
        
        results = []
        
        for target in targets:
            print(f"{Colors.CYAN}   📊 Analyzing: {target}{Colors.END}")
            
            command = [
                'cmseek',
                '-u', target,
                '--batch',  # Non-interactive mode
                '--random-agent' if cmseek_config['random_agent'] else '',
                '--follow-redirect' if cmseek_config['follow_redirect'] else ''
            ]
            
            # Remove empty strings from command
            command = [arg for arg in command if arg]
            
            result = run_command_func(command, f'cmseek_{target.replace("://", "_").replace(":", "_")}.txt', 
                                    f'CMSeek CMS Detection - {target}', 'cmseek')
            results.append(result)
            
            # Parse CMSeek results
            if result['status'] == 'success':
                self._parse_cmseek_results(result['output_file'], target)
        
        return {
            'status': 'success' if any(r['status'] == 'success' for r in results) else 'failed',
            'targets_scanned': len(targets),
            'successful_scans': len([r for r in results if r['status'] == 'success'])
        }
    
    def run_http_enum_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run nmap http-enum script for additional CMS detection"""
        print(f"{Colors.CYAN}🔍 Step 2: Running Nmap http-enum for web enumeration...{Colors.END}")
        
        # Build port list for nmap
        port_list = ','.join(map(str, web_ports))
        
        http_enum_config = self.config.get('http_enum', {
            'timing': 'T4',
            'scripts': 'http-enum,http-headers,http-methods,http-title'
        })
        
        command = [
            'nmap',
            '-sS' if self._check_sudo() else '-sT',
            '-p', port_list,
            '--script', http_enum_config['scripts'],
            f"-{http_enum_config['timing']}",
            target_ip
        ]
        
        result = run_command_func(command, 'nmap_http_enum.txt', 'Nmap HTTP Enumeration & CMS Detection', 'nmap')
        
        # Parse http-enum results
        if result['status'] == 'success':
            self._parse_http_enum_results(result['output_file'])
        
        return result
    
    def run_additional_cms_checks(self, targets: List[str], run_command_func) -> Dict:
        """Run additional CMS-specific checks and vulnerability scanning"""
        print(f"{Colors.CYAN}🔍 Step 3: Running additional CMS-specific checks...{Colors.END}")
        
        results = []
        
        for cms_info in self.detected_cms:
            cms_type = cms_info.get('type', '').lower()
            target = cms_info.get('url', '')
            
            if not target:
                continue
            
            print(f"{Colors.CYAN}   🎯 Running targeted {cms_type.upper()} checks on {target}...{Colors.END}")
            
            # WordPress specific checks
            if 'wordpress' in cms_type or 'wp' in cms_type:
                wp_result = self._run_wordpress_checks(target, run_command_func)
                results.append(wp_result)
            
            # Drupal specific checks
            elif 'drupal' in cms_type:
                drupal_result = self._run_drupal_checks(target, run_command_func)
                results.append(drupal_result)
            
            # Joomla specific checks
            elif 'joomla' in cms_type:
                joomla_result = self._run_joomla_checks(target, run_command_func)
                results.append(joomla_result)
            
            # Generic CMS checks
            else:
                generic_result = self._run_generic_cms_checks(target, cms_type, run_command_func)
                results.append(generic_result)
        
        return {
            'status': 'success' if results else 'skipped',
            'cms_specific_checks': len(results),
            'targeted_scans': len([r for r in results if r['status'] == 'success'])
        }
    
    def _run_wordpress_checks(self, target: str, run_command_func) -> Dict:
        """Run WordPress-specific enumeration"""
        print(f"{Colors.CYAN}     🔧 WordPress enumeration...{Colors.END}")
        
        # Use WPScan if available, otherwise use nmap scripts
        if self._check_tool_available('wpscan'):
            command = [
                'wpscan',
                '--url', target,
                '--enumerate', 'p,t,u',  # plugins, themes, users
                '--random-user-agent',
                '--output', 'wpscan_results.txt'
            ]
            
            return run_command_func(command, 'wordpress_wpscan.txt', f'WordPress WPScan - {target}', 'wpscan')
        else:
            # Fall back to nmap WordPress scripts
            domain = target.split('://')[1].split('/')[0]
            
            command = [
                'nmap',
                '--script', 'http-wordpress-enum,http-wordpress-users,http-wordpress-plugins',
                '-p', '80,443',
                domain
            ]
            
            return run_command_func(command, 'wordpress_nmap.txt', f'WordPress Nmap Scripts - {target}', 'nmap')
    
    def _run_drupal_checks(self, target: str, run_command_func) -> Dict:
        """Run Drupal-specific enumeration"""
        print(f"{Colors.CYAN}     🔧 Drupal enumeration...{Colors.END}")
        
        # Use droopescan if available
        if self._check_tool_available('droopescan'):
            command = [
                'droopescan',
                'scan', 'drupal',
                '-u', target,
                '-t', '10'
            ]
            
            return run_command_func(command, 'drupal_droopescan.txt', f'Drupal Droopescan - {target}', 'droopescan')
        else:
            # Fall back to basic enumeration
            command = [
                'curl',
                '-s',
                f"{target}/CHANGELOG.txt",
                f"{target}/README.txt",
                f"{target}/INSTALL.txt"
            ]
            
            return run_command_func(command, 'drupal_basic.txt', f'Drupal Basic Check - {target}', 'curl')
    
    def _run_joomla_checks(self, target: str, run_command_func) -> Dict:
        """Run Joomla-specific enumeration"""
        print(f"{Colors.CYAN}     🔧 Joomla enumeration...{Colors.END}")
        
        # Use joomscan if available
        if self._check_tool_available('joomscan'):
            command = [
                'joomscan',
                '-u', target,
                '--enumerate-components'
            ]
            
            return run_command_func(command, 'joomla_joomscan.txt', f'Joomla JoomScan - {target}', 'joomscan')
        else:
            # Basic Joomla checks
            command = [
                'curl',
                '-s',
                f"{target}/administrator/",
                f"{target}/README.txt",
                f"{target}/configuration.php-dist"
            ]
            
            return run_command_func(command, 'joomla_basic.txt', f'Joomla Basic Check - {target}', 'curl')
    
    def _run_generic_cms_checks(self, target: str, cms_type: str, run_command_func) -> Dict:
        """Run generic CMS enumeration"""
        print(f"{Colors.CYAN}     🔧 {cms_type.title()} generic enumeration...{Colors.END}")
        
        # Generic CMS enumeration using common paths
        common_paths = [
            '/admin/', '/administrator/', '/wp-admin/', '/admin.php',
            '/login/', '/login.php', '/dashboard/', '/control/',
            '/readme.txt', '/README.txt', '/CHANGELOG.txt',
            '/robots.txt', '/sitemap.xml', '/.htaccess'
        ]
        
        # Use ffuf for directory enumeration if available
        if self._check_tool_available('ffuf'):
            # Create temporary wordlist
            wordlist_file = 'cms_paths.txt'
            with open(wordlist_file, 'w') as f:
                f.write('\n'.join([path.lstrip('/') for path in common_paths]))
            
            command = [
                'ffuf',
                '-u', f"{target}/FUZZ",
                '-w', wordlist_file,
                '-mc', '200,301,302,403',
                '-t', '10',
                '-s'  # Silent mode
            ]
            
            return run_command_func(command, f'cms_enum_{cms_type}.txt', f'{cms_type.title()} Path Enumeration', 'ffuf')
        else:
            # Fall back to curl checks
            command = ['curl', '-s'] + [f"{target}{path}" for path in common_paths]
            
            return run_command_func(command, f'cms_basic_{cms_type}.txt', f'{cms_type.title()} Basic Check', 'curl')
    
    def _parse_cmseek_results(self, output_file: str, target: str):
        """Parse CMSeek results to extract CMS information"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            cms_info = {'url': target, 'source': 'cmseek'}
            
            # Look for CMS detection patterns
            import re
            
            # CMSeek patterns
            cms_patterns = [
                (r'CMS:\s*(\w+)', 'type'),
                (r'Version:\s*([^\n]+)', 'version'),
                (r'Detected CMS:\s*(\w+)', 'type'),
                (r'WordPress.*?(\d+\.\d+(?:\.\d+)?)', 'version'),
                (r'Joomla.*?(\d+\.\d+(?:\.\d+)?)', 'version'),
                (r'Drupal.*?(\d+\.\d+(?:\.\d+)?)', 'version')
            ]
            
            for pattern, key in cms_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    cms_info[key] = match.group(1)
            
            # Look for vulnerabilities
            vuln_indicators = [
                'vulnerability', 'exploit', 'CVE-', 'security issue',
                'outdated', 'insecure', 'weak'
            ]
            
            for indicator in vuln_indicators:
                if indicator.lower() in content.lower():
                    cms_info['potential_vulnerabilities'] = True
                    break
            
            if 'type' in cms_info:
                self.detected_cms.append(cms_info)
                print(f"{Colors.GREEN}   ✅ CMS detected: {cms_info.get('type', 'Unknown')} on {target}{Colors.END}")
                
                if 'version' in cms_info:
                    print(f"{Colors.GREEN}      Version: {cms_info['version']}{Colors.END}")
        
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse CMSeek results: {e}{Colors.END}")
    
    def _parse_http_enum_results(self, output_file: str):
        """Parse nmap http-enum results"""
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Look for http-enum findings
            import re
            
            # Extract interesting directories and files
            enum_patterns = [
                r'http-enum:\s*(.+)',
                r'Interesting directory w/ listing on \d+/tcp:\s*(.+)',
                r'Interesting file on \d+/tcp:\s*(.+)',
                r'/([^/\s]+/).*?\(Status: \d+\)'
            ]
            
            for pattern in enum_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match.strip():
                        self.http_enum_results.append(match.strip())
                        print(f"{Colors.GREEN}   ✅ HTTP enum found: {match.strip()}{Colors.END}")
            
            # Look for CMS indicators in http-enum
            cms_indicators = {
                'wordpress': ['wp-content', 'wp-admin', 'wp-includes', 'wp-login'],
                'joomla': ['administrator', 'joomla', 'components', 'modules'],
                'drupal': ['sites/default', 'misc', 'modules', 'themes', 'drupal'],
                'magento': ['skin/frontend', 'js/mage', 'magento'],
                'prestashop': ['prestashop', 'ps_'],
                'opencart': ['opencart', 'catalog/view']
            }
            
            for cms, indicators in cms_indicators.items():
                if any(indicator in content.lower() for indicator in indicators):
                    cms_info = {
                        'type': cms,
                        'source': 'http-enum',
                        'confidence': 'medium'
                    }
                    
                    # Check if already detected by CMSeek
                    if not any(c['type'].lower() == cms for c in self.detected_cms):
                        self.detected_cms.append(cms_info)
                        print(f"{Colors.GREEN}   ✅ CMS detected by http-enum: {cms.title()}{Colors.END}")
        
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not parse http-enum results: {e}{Colors.END}")
    
    def _check_tool_available(self, tool: str) -> bool:
        """Check if a tool is available"""
        try:
            subprocess.run(['which', tool], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _check_sudo(self) -> bool:
        """Check if sudo is available"""
        try:
            subprocess.run(['sudo', '-n', 'true'], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def comprehensive_cms_scan(self, target_ip: str, web_ports: List[int], run_command_func) -> Dict:
        """Run comprehensive CMS detection and enumeration"""
        if not self.should_run_cms_scan(web_ports):
            return {'status': 'skipped', 'reason': 'No web services detected'}
        
        targets = self.get_web_targets(target_ip, web_ports)
        
        print(f"{Colors.GREEN}🎯 Running Comprehensive CMS Detection & Enumeration{Colors.END}")
        print(f"{Colors.CYAN}🌐 Targets: {len(targets)} web service(s){Colors.END}")
        print(f"{Colors.CYAN}🔍 Phase 1: CMS Detection (CMSeek){Colors.END}")
        print(f"{Colors.CYAN}📊 Phase 2: HTTP Enumeration (Nmap){Colors.END}")
        print(f"{Colors.CYAN}🎯 Phase 3: CMS-Specific Testing{Colors.END}")
        
        results = {
            'targets': targets,
            'phases': {}
        }
        
        # Phase 1: CMSeek Detection
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Phase 1: CMS Detection with CMSeek{Colors.END}")
        
        cmseek_result = self.run_cmseek_scan(targets, run_command_func)
        results['phases']['cmseek'] = cmseek_result
        
        # Phase 2: HTTP Enumeration
        print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Phase 2: HTTP Enumeration with Nmap{Colors.END}")
        
        http_enum_result = self.run_http_enum_scan(target_ip, web_ports, run_command_func)
        results['phases']['http_enum'] = http_enum_result
        
        # Phase 3: CMS-Specific Testing
        print(f"\n{Colors.BOLD}{Colors.BLUE}🎯 Phase 3: CMS-Specific Testing{Colors.END}")
        
        if self.detected_cms:
            cms_specific_result = self.run_additional_cms_checks(targets, run_command_func)
            results['phases']['cms_specific'] = cms_specific_result
        else:
            print(f"{Colors.YELLOW}⚠️  No CMS detected - skipping CMS-specific tests{Colors.END}")
            results['phases']['cms_specific'] = {'status': 'skipped', 'reason': 'No CMS detected'}
        
        # Generate comprehensive report
        self._generate_comprehensive_cms_report(results)
        
        # Determine overall status
        if self.detected_cms:
            results['status'] = 'cms_detected'
            results['cms_count'] = len(self.detected_cms)
            results['detected_cms'] = [cms['type'] for cms in self.detected_cms]
        else:
            results['status'] = 'no_cms_detected'
            results['message'] = 'No CMS systems detected on target'
        
        return results
    
    def _generate_comprehensive_cms_report(self, results: Dict):
        """Generate a comprehensive CMS detection and enumeration report"""
        report_file = 'cms_comprehensive_report.txt'
        
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("ipsnipe Comprehensive CMS Detection & Enumeration Report\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Targets Scanned: {len(results['targets'])}\n")
            f.write(f"Scan Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # CMS Detection Summary
            f.write("🎯 CMS DETECTION SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total CMS Systems Detected: {len(self.detected_cms)}\n\n")
            
            if self.detected_cms:
                f.write("Detected CMS Systems:\n")
                for cms in self.detected_cms:
                    f.write(f"  • {cms.get('type', 'Unknown').title()}")
                    if 'version' in cms:
                        f.write(f" (Version: {cms['version']})")
                    if 'url' in cms:
                        f.write(f" - {cms['url']}")
                    f.write(f" [Source: {cms.get('source', 'unknown')}]\n")
                    
                    if cms.get('potential_vulnerabilities'):
                        f.write(f"    ⚠️  Potential security issues detected\n")
                f.write("\n")
            else:
                f.write("No CMS systems detected.\n\n")
            
            # HTTP Enumeration Results
            f.write("📊 HTTP ENUMERATION RESULTS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Interesting Paths/Files Found: {len(self.http_enum_results)}\n\n")
            
            if self.http_enum_results:
                f.write("Discovered Paths/Files:\n")
                for result in self.http_enum_results[:20]:  # Limit to first 20
                    f.write(f"  • {result}\n")
                if len(self.http_enum_results) > 20:
                    f.write(f"  ... and {len(self.http_enum_results) - 20} more entries\n")
                f.write("\n")
            
            # Security Recommendations
            f.write("🔐 SECURITY RECOMMENDATIONS\n")
            f.write("-" * 40 + "\n")
            
            if self.detected_cms:
                f.write("Based on detected CMS systems:\n")
                
                unique_cms = list(set(cms['type'].lower() for cms in self.detected_cms if 'type' in cms))
                
                for cms_type in unique_cms:
                    if 'wordpress' in cms_type:
                        f.write("  📝 WordPress Security:\n")
                        f.write("    • Keep WordPress core, themes, and plugins updated\n")
                        f.write("    • Use strong admin passwords and 2FA\n")
                        f.write("    • Consider security plugins (Wordfence, Sucuri)\n")
                        f.write("    • Hide wp-admin from unauthorized access\n\n")
                    
                    elif 'joomla' in cms_type:
                        f.write("  📝 Joomla Security:\n")
                        f.write("    • Keep Joomla core and extensions updated\n")
                        f.write("    • Secure administrator directory\n")
                        f.write("    • Use strong passwords and enable 2FA\n")
                        f.write("    • Regular security audits\n\n")
                    
                    elif 'drupal' in cms_type:
                        f.write("  📝 Drupal Security:\n")
                        f.write("    • Keep Drupal core and modules updated\n")
                        f.write("    • Follow Drupal security best practices\n")
                        f.write("    • Regular security updates are critical\n")
                        f.write("    • Secure file permissions\n\n")
            else:
                f.write("  • Implement web application security headers\n")
                f.write("  • Regular security assessments\n")
                f.write("  • Keep web server software updated\n")
                f.write("  • Monitor for unauthorized changes\n\n")
            
            # Tool Execution Summary
            f.write("🔧 TOOL EXECUTION SUMMARY\n")
            f.write("-" * 40 + "\n")
            for phase, result in results['phases'].items():
                status = result.get('status', 'unknown')
                f.write(f"  {phase.replace('_', ' ').title()}: {status.upper()}\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("For detailed results, check individual tool output files.\n")
            f.write("=" * 80 + "\n")
        
        print(f"{Colors.GREEN}📄 Comprehensive CMS report generated: {report_file}{Colors.END}") 