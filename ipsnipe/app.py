#!/usr/bin/env python3
"""
Main ipsnipe application class
Orchestrates all components and handles the scanning workflow
"""

import sys
from typing import Dict, List
from pathlib import Path
from .core.config import ConfigManager
from .ui.colors import print_banner, console
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
            console.print("⚠️  Advanced DNS scanner not available", style="yellow")
            self.advanced_dns_scanner = None
            
        try:
            from .scanners.enhanced_web_scanner import EnhancedWebScanner
            self.enhanced_web_scanner = EnhancedWebScanner(self.config)
        except ImportError:
            console.print("⚠️  Enhanced web scanner not available", style="yellow")
            self.enhanced_web_scanner = None
    
    def run_command(self, command: List[str], output_file: str, description: str, scan_type: str = "generic") -> Dict:
        """Delegate command execution to scanner core"""
        return self.scanner_core.run_command(command, output_file, description, scan_type)
    
    def _auto_discover_web_ports_and_domains(self):
        """Auto-discover web ports and domains when no nmap scan has been run"""
        console.print("\n🔍 Web-only scan detected - performing automatic web port discovery", style="bold yellow")
        console.print("💡 No nmap scan performed yet, checking common web ports automatically...", style="cyan")
        
        # Common web ports to check
        common_web_ports = [80, 443, 8080, 8443, 8000, 8888, 3000, 5000, 8008]
        
        console.print(f"🌐 Testing common web ports: {common_web_ports}", style="cyan")
        
        # Use web detector to find responsive web services
        web_result = self.web_detector.quick_web_check(self.target_ip, common_web_ports)
        
        if web_result['has_web_services']:
            self.web_ports.extend(web_result['web_ports'])
            self.open_ports.extend(web_result['web_ports'])  # Also add to general open ports list
            
            console.print(f"✅ Found responsive web services on: {web_result['web_ports']}", style="green")
            
            # Now run domain discovery since we found web services
            console.print("🚀 Running domain discovery on detected web services...", style="cyan")
            domains_added = self._run_automatic_domain_discovery()
            
            # Configure wordlist manager even if domains weren't added
            if self.wordlist_manager and not domains_added:
                self.wordlist_manager.set_web_ports(web_result['web_ports'])
                if hasattr(self.web_scanners, 'set_wordlist_manager'):
                    self.web_scanners.set_wordlist_manager(self.wordlist_manager)
                    console.print("🔧 Web scanners configured with wordlist manager", style="cyan")
            
            return True
        else:
            console.print("⚠️  No responsive web services found on common ports", style="yellow")
            console.print("💡 Web tools will be skipped - consider running nmap first for comprehensive port discovery", style="cyan")
            return False
    
    def _run_automatic_domain_discovery(self) -> bool:
        """Automatically run domain discovery with minimal output"""
        if not self.web_ports or not self.domain_manager:
            return False
        
        # Web detection and domain discovery
        web_result = self.web_detector.quick_web_check(self.target_ip, self.web_ports)
        confirmed_web_ports = web_result['web_ports'] if web_result['has_web_services'] else self.web_ports
        
        discovered_domains = self.domain_manager.discover_domains_with_whatweb(self.target_ip, confirmed_web_ports)
        
        if discovered_domains:
            self.discovered_domains.extend(discovered_domains)
            
            # Backup and update hosts file
            self.domain_manager.backup_hosts_file()
            hosts_updated = self.domain_manager.add_domains_to_hosts(discovered_domains)
            
            if hosts_updated:
                # Configure scanners
                working_domains = self.domain_manager.verify_domain_resolution(discovered_domains)
                best_domain = self.domain_manager.get_best_domain(working_domains)
                
                if best_domain and hasattr(self.web_scanners, 'set_primary_domain'):
                    self.web_scanners.set_primary_domain(best_domain)
                
                # Configure wordlist manager
                if self.wordlist_manager:
                    self.wordlist_manager.set_discovered_domains(discovered_domains)
                    self.wordlist_manager.set_web_ports(confirmed_web_ports)
                    
                    if hasattr(self.web_scanners, 'set_wordlist_manager'):
                        self.web_scanners.set_wordlist_manager(self.wordlist_manager)
                
                return True
        
        return False
    
    def run_attacks(self, selected_attacks: List[str], port_range: str = None):
        """Execute Full Sniper Mode reconnaissance with minimal output"""
        # Show scan start notification
        console.print("\n🚀 Full Sniper Mode Started", style="bold red")
        console.print(f"Target: {self.target_ip} | Tools: {len(selected_attacks)} | Controls: 's'=skip, 'q'=quit", style="cyan")
        
        # Execute all selected scans
        total_scans = len(selected_attacks)
        current_scan_num = 0
        domains_added_to_hosts = False
        first_nmap_completed = False
        
        for attack in selected_attacks:
            current_scan_num += 1
            
            # Simple progress indicator
            console.print(f"\n[{current_scan_num}/{total_scans}] {attack.replace('_', ' ').title()}", style="bold", end=' ')
            
            # Add start time
            start_time = __import__('time').time()
            if attack == 'nmap_full':
                self.results[attack] = self.nmap_scanner.full_scan(
                    self.target_ip, self.run_command, port_range
                )
                # Update port tracking
                self.open_ports.extend(self.nmap_scanner.get_open_ports())
                self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
                # Enhanced web port detection for common scenarios
                if not self.nmap_scanner.get_web_ports() and any(p in [80, 443, 8080, 8443] for p in self.nmap_scanner.get_open_ports()):
                    self.nmap_scanner.detect_web_services_by_response(self.target_ip)
                    self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
                # Auto domain discovery when web ports found
                if self.web_ports and not domains_added_to_hosts:
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
                        console.print(f"🎯 DNS enumeration found {len(new_subdomains)} additional subdomains", style="green")
                        
                        # Add new subdomains to hosts file
                        if self.domain_manager:
                            hosts_updated_dns = self.domain_manager.add_domains_to_hosts(new_subdomains)
                            if hosts_updated_dns:
                                console.print("✅ New subdomains added to /etc/hosts", style="green")
                                # Update our discovered domains list
                                self.discovered_domains.extend(new_subdomains)
                else:
                    console.print("⚠️  DNS enumeration works best after domain discovery", style="yellow")
                    console.print("💡 Try running nmap first to discover domains, or provide a domain manually", style="cyan")
                    
                    # Allow manual domain input for DNS enumeration
                    from rich.prompt import Prompt
                    manual_domain = Prompt.ask("Enter domain for DNS enumeration (or press Enter to skip)", default="").strip()
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
                                console.print(f"🎯 DNS enumeration found {len(new_subdomains)} subdomains", style="green")
                                
                                if self.domain_manager:
                                    hosts_updated_dns = self.domain_manager.add_domains_to_hosts([manual_domain] + new_subdomains)
                                    if hosts_updated_dns:
                                        console.print("✅ Domains added to /etc/hosts", style="green")
                                        self.discovered_domains.extend([manual_domain] + new_subdomains)
                        else:
                            console.print("❌ Invalid domain format", style="red")
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
                            console.print(f"🎯 Advanced DNS enumeration found {len(new_domains)} new domains", style="green")
                            
                            # Add to hosts file if we have domain manager
                            if self.domain_manager:
                                hosts_updated = self.domain_manager.add_domains_to_hosts(new_domains)
                                if hosts_updated:
                                    console.print("✅ New domains added to /etc/hosts", style="green")
                                    self.discovered_domains.extend(new_domains)
                    else:
                        console.print("⚠️  Advanced DNS enumeration works best after domain discovery. Running nmap_quick first is recommended.", style="yellow")
                        self.results[attack] = {'status': 'skipped', 'reason': 'No domains available for enumeration'}
                else:
                    console.print("❌ Advanced DNS scanner not available", style="red")
                    self.results[attack] = {'status': 'error', 'reason': 'Advanced DNS scanner not initialized'}
            
            elif attack == 'enhanced_web':
                # Enhanced web discovery
                if self.enhanced_web_scanner:
                    # Auto-discover web ports if none available
                    active_web_ports = self.web_ports if self.web_ports else []
                    
                    if not active_web_ports:
                        console.print("🌐 No web ports discovered yet, performing quick web port detection...", style="cyan")
                        if self._auto_discover_web_ports_and_domains():
                            active_web_ports = self.web_ports
                    
                    if active_web_ports:
                        self.results[attack] = self.enhanced_web_scanner.comprehensive_discovery(
                            self.target_ip, active_web_ports, self.discovered_domains, self.run_command
                        )
                    else:
                        console.print("⚠️  No web services found for enhanced web discovery", style="yellow")
                        self.results[attack] = {'status': 'skipped', 'reason': 'No web services available'}
                else:
                    console.print("❌ Enhanced web scanner not available", style="red")
                    self.results[attack] = {'status': 'error', 'reason': 'Enhanced web scanner not initialized'}
            
            elif attack == 'theharvester':
                # Use discovered domains if available, otherwise fallback to IP
                if self.discovered_domains:
                    # Run theHarvester against the primary discovered domain
                    primary_domain = self.discovered_domains[0]
                    console.print(f"🌐 Running theHarvester against discovered domain: {primary_domain}", style="green")
                    self.results[attack] = self.dns_scanner.theharvester_domain_scan(
                        primary_domain, self.run_command
                    )
                else:
                    self.results[attack] = self.dns_scanner.theharvester_scan(
                        self.target_ip, self.run_command
                    )
            

            
            # Final safety check: Force domain discovery if we have web ports but haven't run it yet
            if not domains_added_to_hosts and self.web_ports:
                console.print("🔄 Final check: Web ports detected but domain discovery not run yet - running now...", style="yellow")
                domains_added_to_hosts = self._run_automatic_domain_discovery()
            
            # Show simple status and handle user quit
            if attack in self.results:
                status = self.results[attack]['status']
                elapsed = __import__('time').time() - start_time
                
                if status == 'user_quit':
                    console.print("- Quit requested")
                    break  # Exit the scan loop
                elif status == 'skipped':
                    console.print("- Skipped", style="yellow")
                elif status == 'success':
                    console.print(f"- Done ({elapsed:.0f}s)", style="green")
                elif status == 'failed':
                    console.print("- Failed", style="red")
                elif status == 'timeout':
                    console.print("- Timeout", style="yellow")
                elif status == 'not_found':
                    console.print("- Tool not found", style="red")
                elif status == 'error':
                    console.print("- Error", style="red")
                else:
                    console.print(f"- {status}")
        
        # Stop input monitoring
        if self.scanner_core:
            self.scanner_core.stop_input_monitor()
        
        # Remove duplicates from port lists
        self.open_ports = sorted(list(set(self.open_ports)))
        self.web_ports = sorted(list(set(self.web_ports)))
        
        # Generate summary report
        self.report_generator.generate_summary_report(
            self.target_ip, self.results, self.open_ports, self.web_ports, self.discovered_domains
        )
        
        # Show concise completion summary
        successful_scans = len([r for r in self.results.values() if r.get('status') == 'success'])
        user_quit = any(r.get('status') == 'user_quit' for r in self.results.values())
        
        console.print("\n✅ Full Sniper Mode Complete", style="bold red")
        console.print(f"Results: {successful_scans}/{len(selected_attacks)} tools successful", style="cyan")
        
        # Show key findings
        findings = []
        if self.open_ports:
            findings.append(f"{len(self.open_ports)} open ports")
        if self.web_ports:
            findings.append(f"{len(self.web_ports)} web services")
        if self.discovered_domains:
            findings.append(f"{len(self.discovered_domains)} domains")
        
        if findings:
            console.print(f"Found: {', '.join(findings)}", style="green")
        
        # Show output location
        console.print(f"Output: {Path(self.output_dir).name}", style="cyan")
        console.print("Reports: FINDINGS.md, SUMMARY.md", style="cyan")
        
        # Show domain info if discovered
        if self.discovered_domains:
            console.print("💡 Domains added to /etc/hosts for continued access", style="yellow")
    
    def run(self):
        """Main execution method"""
        try:
            # Show ethical disclaimer first (unless skipped)
            if not self.skip_disclaimer:
                self.ui.show_disclaimer()
            else:
                console.print("⚠️  Disclaimer skipped - Remember to use this tool ethically and legally!\n", style="yellow")
            
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
                console.print("👋 Reconnaissance cancelled.", style="yellow")
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            if self.scanner_core and self.scanner_core.current_process:
                console.print("\n🛑 Stopping current scan...", style="yellow")
                self.scanner_core._terminate_process()
                self.scanner_core.stop_input_monitor()
            console.print("\n👋 ipsnipe interrupted by user. Goodbye!", style="yellow")
            sys.exit(0)
        except Exception as e:
            console.print(f"\n❌ An error occurred: {str(e)}", style="red")
            sys.exit(1) 