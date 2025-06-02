#!/usr/bin/env python3
"""
Main ipsnipe application class
Orchestrates all components and handles the scanning workflow
"""

import sys
from typing import Dict, List
from .core.config import ConfigManager
from .ui.colors import Colors, print_banner
from .ui.interface import UserInterface
from .core.scanner_core import ScannerCore
from .scanners import NmapScanner, WebScanners, DNSScanner, WordlistManager
from .scanners.web_detection import WebDetector
from .scanners.domain_manager import DomainManager
from .scanners.param_lfi_scanner import ParameterLFIScanner
from .scanners.cms_scanner import CMSScanner
from .core.report_generator import ReportGenerator


class IPSnipeApp:
    """Main ipsnipe application"""
    
    def __init__(self, skip_disclaimer: bool = False, sudo_mode: bool = None):
        self.skip_disclaimer = skip_disclaimer
        self.sudo_mode = sudo_mode
        self.target_ip = None
        self.output_dir = None
        self.enhanced_mode = False
        self.results = {}
        
        # Load configuration
        self.config = ConfigManager.load_config()
        
        # Initialize components
        self.ui = UserInterface()
        self.scanner_core = None  # Will be initialized after output_dir is set
        self.nmap_scanner = None  # Will be initialized after enhanced_mode is set
        self.web_scanners = None
        self.dns_scanner = None
        self.web_detector = WebDetector()
        self.domain_manager = None
        self.param_lfi_scanner = None
        self.cms_scanner = None
        self.report_generator = None
        self.wordlist_manager = None  # Will be initialized after output_dir is set
        
        # Port and domain tracking
        self.open_ports = []
        self.web_ports = []
        self.discovered_domains = []
    
    def initialize_scanners(self):
        """Initialize scanner components after configuration is complete"""
        self.scanner_core = ScannerCore(self.config, self.output_dir)
        self.nmap_scanner = NmapScanner(self.config, self.enhanced_mode)
        self.web_scanners = WebScanners(self.config)
        self.dns_scanner = DNSScanner(self.config)
        self.domain_manager = DomainManager(self.target_ip, self.enhanced_mode)
        self.param_lfi_scanner = ParameterLFIScanner(self.config)
        self.cms_scanner = CMSScanner(self.config)
        self.report_generator = ReportGenerator(self.output_dir)
        self.wordlist_manager = WordlistManager(self.config, self.output_dir)
        
        # Initialize enhanced scanners
        try:
            from .scanners.advanced_dns_scanner import AdvancedDNSScanner
            self.advanced_dns_scanner = AdvancedDNSScanner(self.config)
        except ImportError:
            print(f"{Colors.YELLOW}⚠️  Advanced DNS scanner not available{Colors.END}")
            self.advanced_dns_scanner = None
            
        try:
            from .scanners.enhanced_web_scanner import EnhancedWebScanner
            self.enhanced_web_scanner = EnhancedWebScanner(self.config)
        except ImportError:
            print(f"{Colors.YELLOW}⚠️  Enhanced web scanner not available{Colors.END}")
            self.enhanced_web_scanner = None
    
    def run_command(self, command: List[str], output_file: str, description: str, scan_type: str = "generic") -> Dict:
        """Delegate command execution to scanner core"""
        return self.scanner_core.run_command(command, output_file, description, scan_type)
    
    def _auto_discover_web_ports_and_domains(self):
        """Auto-discover web ports and domains when no nmap scan has been run"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}🔍 Web-only scan detected - performing automatic web port discovery{Colors.END}")
        print(f"{Colors.CYAN}💡 No nmap scan performed yet, checking common web ports automatically...{Colors.END}")
        
        # Common web ports to check
        common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 3000, 5000, 8008]
        
        print(f"{Colors.CYAN}🌐 Testing common web ports: {common_web_ports}{Colors.END}")
        
        # Use web detector to find responsive web services
        web_result = self.web_detector.quick_web_check(self.target_ip, common_web_ports)
        
        if web_result['has_web_services']:
            self.web_ports.extend(web_result['web_ports'])
            self.open_ports.extend(web_result['web_ports'])  # Also add to general open ports list
            
            print(f"{Colors.GREEN}✅ Found responsive web services on: {web_result['web_ports']}{Colors.END}")
            
            # Now run domain discovery since we found web services
            print(f"{Colors.CYAN}🚀 Running domain discovery on detected web services...{Colors.END}")
            domains_added = self._run_automatic_domain_discovery()
            
            # Configure wordlist manager even if domains weren't added
            if self.wordlist_manager and not domains_added:
                self.wordlist_manager.set_web_ports(web_result['web_ports'])
                if hasattr(self.web_scanners, 'set_wordlist_manager'):
                    self.web_scanners.set_wordlist_manager(self.wordlist_manager)
                    print(f"{Colors.CYAN}🔧 Web scanners configured with wordlist manager{Colors.END}")
            
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  No responsive web services found on common ports{Colors.END}")
            print(f"{Colors.CYAN}💡 Web tools will be skipped - consider running nmap first for comprehensive port discovery{Colors.END}")
            return False
    
    def _run_automatic_domain_discovery(self) -> bool:
        """Automatically run domain discovery and enhanced nmap when web ports are found"""
        if not self.web_ports or not self.domain_manager:
            print(f"{Colors.YELLOW}⚠️  Skipping domain discovery - no web ports or domain manager not initialized{Colors.END}")
            return False
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 HTB-Optimized Domain Discovery Phase{Colors.END}")
        print("-" * 60)
        print(f"{Colors.GREEN}🎯 Web ports detected: {self.web_ports}{Colors.END}")
        print(f"{Colors.CYAN}🔍 Running whatweb to capture HTTP headers and discover domains{Colors.END}")
        print(f"{Colors.CYAN}   Looking for: *.htb, *.local, *.box domains, redirects, headers{Colors.END}")
        
        # Show sudo status for hosts file operations
        if self.enhanced_mode:
            print(f"{Colors.GREEN}🔧 Enhanced mode enabled - will use sudo for /etc/hosts operations{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Standard mode - /etc/hosts operations may require manual intervention{Colors.END}")
        
        # Step 1: Run whatweb for domain discovery (primary method for HTB)
        print(f"{Colors.CYAN}🌐 Step 1: Running whatweb scan to capture headers and domains...{Colors.END}")
        
        # First run web detection to confirm responsive services
        web_result = self.web_detector.quick_web_check(self.target_ip, self.web_ports)
        if web_result['has_web_services']:
            print(f"{Colors.GREEN}✅ Web detection confirmed {len(web_result['services'])} responsive web service(s){Colors.END}")
            # Update web ports with confirmed responsive ones
            confirmed_web_ports = web_result['web_ports']
        else:
            print(f"{Colors.YELLOW}⚠️  Web detection found no responsive services, using nmap-detected ports{Colors.END}")
            confirmed_web_ports = self.web_ports
        
        # Step 2: Run whatweb domain discovery on confirmed web ports
        print(f"{Colors.CYAN}🔍 Step 2: Whatweb analyzing {confirmed_web_ports} for domain discovery...{Colors.END}")
        discovered_domains = self.domain_manager.discover_domains_with_whatweb(self.target_ip, confirmed_web_ports)
        
        if discovered_domains:
            print(f"{Colors.GREEN}🎯 Step 3: Domains discovered by whatweb: {discovered_domains}{Colors.END}")
            self.discovered_domains.extend(discovered_domains)
            
            # Step 4: Backup hosts file
            print(f"{Colors.CYAN}🛡️  Step 4: Creating /etc/hosts backup...{Colors.END}")
            self.domain_manager.backup_hosts_file()
            
            # Step 5: Add domains to hosts file
            print(f"{Colors.CYAN}📝 Step 5: Adding domains to /etc/hosts...{Colors.END}")
            hosts_updated = self.domain_manager.add_domains_to_hosts(discovered_domains)
            
            if hosts_updated:
                print(f"{Colors.GREEN}✅ /etc/hosts updated successfully{Colors.END}")
                
                # Verify domain resolution
                working_domains = self.domain_manager.verify_domain_resolution(discovered_domains)
                
                # Get the best domain for scanning
                best_domain = self.domain_manager.get_best_domain(working_domains)
                
                if best_domain:
                    print(f"{Colors.GREEN}🎯 Primary domain for scanning: {best_domain}{Colors.END}")
                    
                    # Automatically run enhanced nmap scan with domain on discovered ports
                    if self.open_ports:
                        print(f"\n{Colors.YELLOW}🔄 Running enhanced nmap scan with domain name for better service detection...{Colors.END}")
                        
                        port_list = ','.join(map(str, sorted(set(self.open_ports))))
                        
                        # Run enhanced nmap scan with domain
                        nmap_domain_result = self.nmap_scanner.domain_enhanced_scan(
                            best_domain, self.run_command, port_list
                        )
                        
                        if nmap_domain_result:
                            self.results['nmap_domain_enhanced'] = nmap_domain_result
                            print(f"{Colors.GREEN}✅ Enhanced domain scan completed{Colors.END}")
                            print(f"{Colors.CYAN}📄 Check nmap_domain_enhanced_*.txt for website names and service details{Colors.END}")
                    
                    # Update web scanners to use domain names
                    if hasattr(self.web_scanners, 'set_primary_domain'):
                        self.web_scanners.set_primary_domain(best_domain)
                        print(f"{Colors.CYAN}🔧 Web scanners configured to use domain: {best_domain}{Colors.END}")
                    
                    # Step 6: Comprehensive DNS enumeration
                    print(f"{Colors.CYAN}🔍 Step 6: Running comprehensive DNS enumeration...{Colors.END}")
                    dns_result = self.dns_scanner.comprehensive_dns_enumeration(
                        self.target_ip, discovered_domains, self.run_command
                    )
                    
                    # Add newly discovered subdomains to hosts file
                    if dns_result.get('status') == 'success' and dns_result.get('new_domains'):
                        new_subdomains = dns_result['new_domains']
                        print(f"{Colors.GREEN}🎯 DNS enumeration found {len(new_subdomains)} additional subdomains{Colors.END}")
                        
                        # Add new subdomains to hosts file
                        hosts_updated_dns = self.domain_manager.add_domains_to_hosts(new_subdomains)
                        if hosts_updated_dns:
                            print(f"{Colors.GREEN}✅ New subdomains added to /etc/hosts{Colors.END}")
                            # Update our discovered domains list
                            self.discovered_domains.extend(new_subdomains)
                            discovered_domains.extend(new_subdomains)  # Also update local list
                        
                        # Store DNS enumeration results
                        self.results['dns_enumeration'] = dns_result
                    
                    # Configure wordlist manager with discovered domains and web ports
                    if self.wordlist_manager:
                        self.wordlist_manager.set_discovered_domains(discovered_domains)
                        self.wordlist_manager.set_web_ports(confirmed_web_ports)
                        print(f"{Colors.CYAN}🔧 Wordlist manager configured with discovered domains{Colors.END}")
                        
                        # Connect wordlist manager to web scanners
                        if hasattr(self.web_scanners, 'set_wordlist_manager'):
                            self.web_scanners.set_wordlist_manager(self.wordlist_manager)
                            print(f"{Colors.CYAN}🔧 Web scanners configured with wordlist manager{Colors.END}")
                    
                    print()  # Add spacing
                    return True
            else:
                print(f"{Colors.YELLOW}⚠️  Could not update /etc/hosts - continuing with IP-based scanning{Colors.END}")
        else:
            print(f"{Colors.YELLOW}ℹ️  No domain names discovered from whatweb/HTTP responses{Colors.END}")
            print(f"{Colors.CYAN}💡 This is normal for some targets - continuing with IP-based scanning{Colors.END}")
        
        print()  # Add spacing
        return False
    
    def run_attacks(self, selected_attacks: List[str], port_range: str = None):
        """Execute selected attacks with optional port range"""
        timeout_mins = self.config['general']['scan_timeout'] // 60
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Starting reconnaissance on {self.target_ip}...{Colors.END}")
        print(f"{Colors.CYAN}📋 {len(selected_attacks)} scan(s) selected (timeout: {timeout_mins} minutes each){Colors.END}")
        print(f"{Colors.PURPLE}⏸️  During scans: Press 's' + Enter to skip current scan, 'q' + Enter to quit all{Colors.END}\n")
        
        # Get port range for nmap scans if needed
        nmap_scans = ['nmap_quick', 'nmap_full', 'nmap_udp']
        has_nmap_scans = any(scan in selected_attacks for scan in nmap_scans)
        
        if has_nmap_scans and not port_range:
            port_range = self.ui.get_port_range_input()
        
        # Execute all selected scans
        total_scans = len(selected_attacks)
        current_scan_num = 0
        domains_added_to_hosts = False
        first_nmap_completed = False
        
        for attack in selected_attacks:
            current_scan_num += 1
            print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Scan {current_scan_num}/{total_scans}: {attack.replace('_', ' ').title()}{Colors.END}")
            print("-" * 60)
            if attack == 'nmap_quick':
                self.results[attack] = self.nmap_scanner.quick_scan(
                    self.target_ip, self.run_command, port_range
                )
                # Update port tracking
                self.open_ports.extend(self.nmap_scanner.get_open_ports())
                self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
                # Enhanced web port detection for HTB scenarios (HTTP is common)
                if not self.nmap_scanner.get_web_ports() and any(p in [80, 443, 8080, 8443] for p in self.nmap_scanner.get_open_ports()):
                    print(f"{Colors.YELLOW}🔍 No web services detected by nmap, trying response testing on common ports...{Colors.END}")
                    self.nmap_scanner.detect_web_services_by_response(self.target_ip)
                    self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
                # IMMEDIATE whatweb + domain discovery when web ports found (HTB optimized)
                if self.web_ports and not domains_added_to_hosts:
                    print(f"{Colors.GREEN}🌐 Web port(s) discovered: {self.web_ports}{Colors.END}")
                    print(f"{Colors.CYAN}🚀 Immediately triggering whatweb scan for domain discovery...{Colors.END}")
                    domains_added_to_hosts = self._run_automatic_domain_discovery()
                
                first_nmap_completed = True
                
            elif attack == 'nmap_full':
                self.results[attack] = self.nmap_scanner.full_scan(
                    self.target_ip, self.run_command, port_range
                )
                # Update port tracking
                self.open_ports.extend(self.nmap_scanner.get_open_ports())
                self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
                # Enhanced web port detection for HTB scenarios (HTTP is common)
                if not self.nmap_scanner.get_web_ports() and any(p in [80, 443, 8080, 8443] for p in self.nmap_scanner.get_open_ports()):
                    print(f"{Colors.YELLOW}🔍 No web services detected by nmap, trying response testing on common ports...{Colors.END}")
                    self.nmap_scanner.detect_web_services_by_response(self.target_ip)
                    self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
                # IMMEDIATE whatweb + domain discovery when web ports found (HTB optimized)
                if self.web_ports and not domains_added_to_hosts:
                    print(f"{Colors.GREEN}🌐 Web port(s) discovered: {self.web_ports}{Colors.END}")
                    print(f"{Colors.CYAN}🚀 Immediately triggering whatweb scan for domain discovery...{Colors.END}")
                    domains_added_to_hosts = self._run_automatic_domain_discovery()
                
                first_nmap_completed = True
                
            elif attack == 'nmap_udp':
                self.results[attack] = self.nmap_scanner.udp_scan(
                    self.target_ip, self.run_command, port_range
                )
                # Update port tracking
                self.open_ports.extend(self.nmap_scanner.get_open_ports())
                self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
                # Automatically trigger domain discovery if web ports found
                if self.web_ports and not domains_added_to_hosts:
                    domains_added_to_hosts = self._run_automatic_domain_discovery()
                
                first_nmap_completed = True
                

                
            elif attack == 'feroxbuster':
                # Auto-discover web ports if none found yet
                if not self.web_ports:
                    self._auto_discover_web_ports_and_domains()
                
                # Ensure wordlist manager is connected to web scanners
                if self.wordlist_manager and hasattr(self.web_scanners, 'set_wordlist_manager'):
                    self.web_scanners.set_wordlist_manager(self.wordlist_manager)
                
                self.results[attack] = self.web_scanners.feroxbuster_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'ffuf':
                # Auto-discover web ports if none found yet
                if not self.web_ports:
                    self._auto_discover_web_ports_and_domains()
                
                # Ensure wordlist manager is connected to web scanners
                if self.wordlist_manager and hasattr(self.web_scanners, 'set_wordlist_manager'):
                    self.web_scanners.set_wordlist_manager(self.wordlist_manager)
                
                self.results[attack] = self.web_scanners.ffuf_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                

                
            elif attack == 'param_lfi_scan':
                # Auto-discover web ports if none found yet
                if not self.web_ports:
                    self._auto_discover_web_ports_and_domains()
                
                self.results[attack] = self.param_lfi_scanner.comprehensive_param_lfi_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'cms_scan':
                # Auto-discover web ports if none found yet
                if not self.web_ports:
                    self._auto_discover_web_ports_and_domains()
                
                self.results[attack] = self.cms_scanner.comprehensive_cms_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'dns_enumeration':
                # DNS enumeration works best with discovered domains
                if self.discovered_domains:
                    self.results[attack] = self.dns_scanner.comprehensive_dns_enumeration(
                        self.target_ip, self.discovered_domains, self.run_command
                    )
                    
                    # Add newly discovered subdomains to hosts file
                    if (self.results[attack].get('status') == 'success' and 
                        self.results[attack].get('new_domains')):
                        new_subdomains = self.results[attack]['new_domains']
                        print(f"{Colors.GREEN}🎯 DNS enumeration found {len(new_subdomains)} additional subdomains{Colors.END}")
                        
                        # Add new subdomains to hosts file
                        if self.domain_manager:
                            hosts_updated_dns = self.domain_manager.add_domains_to_hosts(new_subdomains)
                            if hosts_updated_dns:
                                print(f"{Colors.GREEN}✅ New subdomains added to /etc/hosts{Colors.END}")
                                # Update our discovered domains list
                                self.discovered_domains.extend(new_subdomains)
                else:
                    print(f"{Colors.YELLOW}⚠️  DNS enumeration works best after domain discovery{Colors.END}")
                    print(f"{Colors.CYAN}💡 Try running nmap first to discover domains, or provide a domain manually{Colors.END}")
                    
                    # Allow manual domain input for DNS enumeration
                    manual_domain = input(f"{Colors.CYAN}Enter domain for DNS enumeration (or press Enter to skip): {Colors.END}").strip()
                    if manual_domain:
                        # Validate domain format
                        if '.' in manual_domain and not manual_domain.startswith('.'):
                            self.results[attack] = self.dns_scanner.comprehensive_dns_enumeration(
                                self.target_ip, [manual_domain], self.run_command
                            )
                            
                            # Add any discovered subdomains to hosts file
                            if (self.results[attack].get('status') == 'success' and 
                                self.results[attack].get('new_domains')):
                                new_subdomains = self.results[attack]['new_domains']
                                print(f"{Colors.GREEN}🎯 DNS enumeration found {len(new_subdomains)} subdomains{Colors.END}")
                                
                                if self.domain_manager:
                                    hosts_updated_dns = self.domain_manager.add_domains_to_hosts([manual_domain] + new_subdomains)
                                    if hosts_updated_dns:
                                        print(f"{Colors.GREEN}✅ Domains added to /etc/hosts{Colors.END}")
                                        self.discovered_domains.extend([manual_domain] + new_subdomains)
                        else:
                            print(f"{Colors.RED}❌ Invalid domain format{Colors.END}")
                            self.results[attack] = {'status': 'skipped', 'reason': 'Invalid domain format'}
                    else:
                        self.results[attack] = {'status': 'skipped', 'reason': 'No domain provided for DNS enumeration'}
                
            elif attack == 'advanced_dns':
                # Advanced DNS enumeration works best with discovered domains
                if self.advanced_dns_scanner:
                    if self.discovered_domains:
                        self.results[attack] = self.advanced_dns_scanner.comprehensive_enumeration(
                            self.target_ip, self.discovered_domains, self.run_command
                        )
                        
                        # Add newly discovered domains to hosts file
                        if (self.results[attack].get('status') == 'completed' and 
                            self.results[attack].get('new_domains')):
                            new_domains = self.results[attack]['new_domains']
                            print(f"{Colors.GREEN}🎯 Advanced DNS enumeration found {len(new_domains)} new domains{Colors.END}")
                            
                            # Add to hosts file if we have domain manager
                            if self.domain_manager:
                                hosts_updated = self.domain_manager.add_domains_to_hosts(new_domains)
                                if hosts_updated:
                                    print(f"{Colors.GREEN}✅ New domains added to /etc/hosts{Colors.END}")
                                    self.discovered_domains.extend(new_domains)
                    else:
                        print(f"{Colors.YELLOW}⚠️  Advanced DNS enumeration works best after domain discovery. Running nmap_quick first is recommended.{Colors.END}")
                        self.results[attack] = {'status': 'skipped', 'reason': 'No domains available for enumeration'}
                else:
                    print(f"{Colors.RED}❌ Advanced DNS scanner not available{Colors.END}")
                    self.results[attack] = {'status': 'error', 'reason': 'Advanced DNS scanner not initialized'}
            
            elif attack == 'enhanced_web':
                # Enhanced web discovery
                if self.enhanced_web_scanner:
                    # Auto-discover web ports if none available
                    active_web_ports = self.web_ports if self.web_ports else []
                    
                    if not active_web_ports:
                        print(f"{Colors.CYAN}🌐 No web ports discovered yet, performing quick web port detection...{Colors.END}")
                        if self._auto_discover_web_ports_and_domains():
                            active_web_ports = self.web_ports
                    
                    if active_web_ports:
                        self.results[attack] = self.enhanced_web_scanner.comprehensive_discovery(
                            self.target_ip, active_web_ports, self.discovered_domains, self.run_command
                        )
                    else:
                        print(f"{Colors.YELLOW}⚠️  No web services found for enhanced web discovery{Colors.END}")
                        self.results[attack] = {'status': 'skipped', 'reason': 'No web services available'}
                else:
                    print(f"{Colors.RED}❌ Enhanced web scanner not available{Colors.END}")
                    self.results[attack] = {'status': 'error', 'reason': 'Enhanced web scanner not initialized'}
            
            elif attack == 'theharvester':
                # Use discovered domains if available, otherwise fallback to IP
                if self.discovered_domains:
                    # Run theHarvester against the primary discovered domain
                    primary_domain = self.discovered_domains[0]
                    print(f"{Colors.GREEN}🌐 Running theHarvester against discovered domain: {primary_domain}{Colors.END}")
                    self.results[attack] = self.dns_scanner.theharvester_domain_scan(
                        primary_domain, self.run_command
                    )
                else:
                    self.results[attack] = self.dns_scanner.theharvester_scan(
                        self.target_ip, self.run_command
                    )
            

            
            # Final safety check: Force domain discovery if we have web ports but haven't run it yet
            if not domains_added_to_hosts and self.web_ports:
                print(f"{Colors.YELLOW}🔄 Final check: Web ports detected but domain discovery not run yet - running now...{Colors.END}")
                domains_added_to_hosts = self._run_automatic_domain_discovery()
            
            # Show results status and handle user quit
            if attack in self.results:
                status = self.results[attack]['status']
                if status == 'user_quit':
                    print(f"\n{Colors.YELLOW}🛑 User requested to quit all scans{Colors.END}")
                    print(f"{Colors.CYAN}📋 Completed {current_scan_num-1}/{total_scans} scans before quitting{Colors.END}")
                    break  # Exit the scan loop
                elif status == 'skipped':
                    print(f"{Colors.YELLOW}⏭️  {attack.replace('_', ' ').title()} - {self.results[attack].get('reason', 'Skipped')}{Colors.END}")
                elif status == 'success':
                    print(f"{Colors.GREEN}✅ {attack.replace('_', ' ').title()} - Completed{Colors.END}")
                elif status == 'failed':
                    print(f"{Colors.RED}❌ {attack.replace('_', ' ').title()} - Failed{Colors.END}")
                elif status == 'timeout':
                    print(f"{Colors.YELLOW}⏰ {attack.replace('_', ' ').title()} - Timed out{Colors.END}")
                elif status == 'not_found':
                    print(f"{Colors.RED}🔍 {attack.replace('_', ' ').title()} - Tool not found{Colors.END}")
                elif status == 'error':
                    print(f"{Colors.RED}💥 {attack.replace('_', ' ').title()} - Error occurred{Colors.END}")
            
            print()  # Add spacing between attacks
        
        # Stop input monitoring
        if self.scanner_core:
            self.scanner_core.stop_input_monitor()
        
        # Remove duplicates from port lists
        self.open_ports = sorted(list(set(self.open_ports)))
        self.web_ports = sorted(list(set(self.web_ports)))
        
        # Leave hosts file entries in place for continued use
        if self.domain_manager and domains_added_to_hosts:
            print(f"\n{Colors.GREEN}💾 Keeping /etc/hosts entries for continued domain resolution{Colors.END}")
            print(f"{Colors.CYAN}💡 Domains will remain accessible for other scans and tools{Colors.END}")
            if self.discovered_domains:
                print(f"{Colors.CYAN}📝 Added domains: {', '.join(self.discovered_domains)}{Colors.END}")
            print(f"{Colors.YELLOW}🧹 To manually remove later: edit /etc/hosts and remove ipsnipe entries{Colors.END}")
            # Commented out cleanup to preserve entries for other scans
            # self.domain_manager.cleanup_hosts_file()
        
        # Generate summary report with domain information
        self.report_generator.generate_summary_report(
            self.target_ip, self.results, self.open_ports, self.web_ports, self.discovered_domains
        )
        
        # Check if all scans completed or if user quit early
        completed_scans = len([r for r in self.results.values() if r.get('status') not in ['user_quit']])
        user_quit = any(r.get('status') == 'user_quit' for r in self.results.values())
        
        if user_quit:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⏹️  Scan session terminated by user{Colors.END}")
            print(f"{Colors.CYAN}📊 Completed {completed_scans}/{total_scans} scans{Colors.END}")
        else:
            print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All scans completed!{Colors.END}")
        
        print(f"{Colors.CYAN}📁 Results saved in: {self.output_dir}{Colors.END}")
        print(f"{Colors.CYAN}🎯 Check FINDINGS.md for key actionable results{Colors.END}")
        print(f"{Colors.CYAN}📋 Check SUMMARY.md for scan overview{Colors.END}")
        
        # Show web service detection summary
        if self.web_ports:
            print(f"{Colors.GREEN}🌐 Web services detected on ports: {self.web_ports}{Colors.END}")
        elif any(scan in selected_attacks for scan in ['feroxbuster', 'ffuf', 'whatweb']):
            print(f"{Colors.YELLOW}⚠️  No web services detected - some HTTP scans were skipped{Colors.END}")
        
        print(f"{Colors.CYAN}💡 Tip: Review individual scan files for detailed results{Colors.END}")
        
        # Show scan session summary
        successful_scans = len([r for r in self.results.values() if r.get('status') == 'success'])
        skipped_scans = len([r for r in self.results.values() if r.get('status') == 'skipped'])
        failed_scans = len([r for r in self.results.values() if r.get('status') in ['failed', 'timeout', 'error', 'not_found']])
        
        print(f"\n{Colors.BOLD}📈 Scan Summary:{Colors.END}")
        if successful_scans > 0:
            print(f"  {Colors.GREEN}✅ Successful: {successful_scans}{Colors.END}")
        if skipped_scans > 0:
            print(f"  {Colors.YELLOW}⏭️  Skipped: {skipped_scans}{Colors.END}")
        if failed_scans > 0:
            print(f"  {Colors.RED}❌ Failed: {failed_scans}{Colors.END}")
    
    def run(self):
        """Main execution method"""
        try:
            # Show ethical disclaimer first (unless skipped)
            if not self.skip_disclaimer:
                self.ui.show_disclaimer()
            else:
                print(f"{Colors.YELLOW}⚠️  Disclaimer skipped - Remember to use this tool ethically and legally!{Colors.END}\n")
            
            # Show banner after disclaimer acceptance
            print_banner()
            
            # Check dependencies
            if not self.scanner_core:
                # Create temporary scanner core for dependency check
                temp_scanner = ScannerCore(self.config, ".")
                temp_scanner.check_dependencies()
            else:
                self.scanner_core.check_dependencies()
            print()
            
            # Get sudo mode preference
            self.enhanced_mode = self.ui.get_sudo_mode_preference(self.sudo_mode)
            
            # Get target IP
            self.target_ip = self.ui.get_target_ip()
            
            # Create output directory
            self.output_dir = self.ui.create_output_directory(self.target_ip)
            
            # Initialize all scanner components now that we have configuration
            self.initialize_scanners()
            
            # Get attack selection
            selected_attacks = self.ui.show_attack_menu()
            
            # Show configuration summary and get confirmation
            if self.ui.show_scan_summary(self.target_ip, self.output_dir, self.enhanced_mode, selected_attacks):
                self.run_attacks(selected_attacks)
            else:
                print(f"{Colors.YELLOW}👋 Reconnaissance cancelled.{Colors.END}")
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            if self.scanner_core and self.scanner_core.current_process:
                print(f"\n{Colors.YELLOW}🛑 Stopping current scan...{Colors.END}")
                self.scanner_core._terminate_process()
                self.scanner_core.stop_input_monitor()
            print(f"\n{Colors.YELLOW}👋 ipsnipe interrupted by user. Goodbye!{Colors.END}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Colors.RED}❌ An error occurred: {str(e)}{Colors.END}")
            sys.exit(1) 