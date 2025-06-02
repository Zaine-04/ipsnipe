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
from .scanners import NmapScanner, WebScanners, DNSScanner
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
        self.report_generator = None
        
        # Port tracking
        self.open_ports = []
        self.web_ports = []
    
    def initialize_scanners(self):
        """Initialize scanner components after configuration is complete"""
        self.scanner_core = ScannerCore(self.config, self.output_dir)
        self.nmap_scanner = NmapScanner(self.config, self.enhanced_mode)
        self.web_scanners = WebScanners(self.config)
        self.dns_scanner = DNSScanner(self.config)
        self.report_generator = ReportGenerator(self.output_dir)
    
    def run_command(self, command: List[str], output_file: str, description: str, scan_type: str = "generic") -> Dict:
        """Delegate command execution to scanner core"""
        return self.scanner_core.run_command(command, output_file, description, scan_type)
    
    def run_attacks(self, selected_attacks: List[str], port_range: str = None):
        """Execute selected attacks with optional port range"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Starting reconnaissance on {self.target_ip}...{Colors.END}")
        print(f"{Colors.CYAN}📋 {len(selected_attacks)} scan(s) selected{Colors.END}")
        print(f"{Colors.PURPLE}⏸️  During scans: Press 's' + Enter to skip current scan, 'q' + Enter to quit all{Colors.END}\n")
        
        # Get port range for nmap scans if needed
        nmap_scans = ['nmap_quick', 'nmap_full', 'nmap_udp']
        has_nmap_scans = any(scan in selected_attacks for scan in nmap_scans)
        
        if has_nmap_scans and not port_range:
            port_range = self.ui.get_port_range_input()
        
        # Execute all selected scans
        total_scans = len(selected_attacks)
        current_scan_num = 0
        
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
                
            elif attack == 'nmap_full':
                self.results[attack] = self.nmap_scanner.full_scan(
                    self.target_ip, self.run_command, port_range
                )
                # Update port tracking
                self.open_ports.extend(self.nmap_scanner.get_open_ports())
                self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
            elif attack == 'nmap_udp':
                self.results[attack] = self.nmap_scanner.udp_scan(
                    self.target_ip, self.run_command, port_range
                )
                # Update port tracking
                self.open_ports.extend(self.nmap_scanner.get_open_ports())
                self.web_ports.extend(self.nmap_scanner.get_web_ports())
                
            elif attack == 'gobuster_common':
                self.results[attack] = self.web_scanners.gobuster_common(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'gobuster_big':
                self.results[attack] = self.web_scanners.gobuster_big(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'feroxbuster':
                self.results[attack] = self.web_scanners.feroxbuster_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'ffuf':
                self.results[attack] = self.web_scanners.ffuf_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'nikto':
                self.results[attack] = self.web_scanners.nikto_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'whatweb':
                self.results[attack] = self.web_scanners.whatweb_scan(
                    self.target_ip, self.web_ports, self.run_command
                )
                
            elif attack == 'theharvester':
                self.results[attack] = self.dns_scanner.theharvester_scan(
                    self.target_ip, self.run_command
                )
                
            elif attack == 'dnsrecon':
                self.results[attack] = self.dns_scanner.dnsrecon_scan(
                    self.target_ip, self.run_command
                )
            
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
        
        # Generate summary report
        self.report_generator.generate_summary_report(
            self.target_ip, self.results, self.open_ports, self.web_ports
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
        print(f"{Colors.CYAN}📋 Check SUMMARY_REPORT.md for an overview{Colors.END}")
        
        # Show web service detection summary
        if self.web_ports:
            print(f"{Colors.GREEN}🌐 Web services detected on ports: {self.web_ports}{Colors.END}")
        elif any(scan in selected_attacks for scan in ['gobuster_common', 'gobuster_big', 'feroxbuster', 'ffuf', 'nikto', 'whatweb']):
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