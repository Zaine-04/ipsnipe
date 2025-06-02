#!/usr/bin/env python3
"""
ipsnipe Demo Script

Demo of ipsnipe for screenshots and testing.

Author: hckerhub (X: @hckerhub)  
Website: https://hackerhub.me
GitHub: https://github.com/hckerhub

This demo showcases all ipsnipe features without performing actual scans.
It simulates the complete reconnaissance workflow and generates sample outputs
that demonstrate the tool's capabilities for presentations or testing.

Key Features Demonstrated:
- Interactive IP validation and menu selection
- Port range configuration 
- Individual tool demonstrations
- Complete reconnaissance workflow simulation
- Sample report generation with realistic security findings
"""

import time
import sys
import datetime
from pathlib import Path

# Import ipsnipe classes
from ipsnipe import ipsnipe, Colors, BANNER

class ipsnipdemo(ipsnipe):
    """Demo version of ipsnipe that simulates scans without running actual commands"""
    
    def __init__(self):
        super().__init__(skip_disclaimer=True)  # Skip disclaimer for demo
        self.demo_mode = True
        # Simulate some discovered ports for web detection demo
        self.demo_open_ports = [22, 80, 443, 3306]
        self.demo_web_ports = [80, 443]
    
    def run_command(self, command, output_file, description, scan_type="generic"):
        """Simulate command execution for demo purposes"""
        timeout = self.config['general']['scan_timeout']
        print(f"{Colors.YELLOW}🔄 Running: {description}... (timeout: {timeout}s) [DEMO]{Colors.END}")
        
        # Simulate execution time
        for i in range(3):
            print(f"{Colors.BLUE}   {'.' * (i + 1)}{Colors.END}")
            time.sleep(0.5)
        
        # Simulate port detection for nmap scans
        if 'nmap' in description.lower():
            self.open_ports = self.demo_open_ports
            self.web_ports = self.demo_web_ports
            print(f"{Colors.GREEN}🔓 Discovered {len(self.demo_open_ports)} open ports: {sorted(self.demo_open_ports)} [DEMO]{Colors.END}")
            print(f"{Colors.CYAN}🌐 Detected {len(self.demo_web_ports)} web services on ports: {sorted(self.demo_web_ports)} [DEMO]{Colors.END}")
        
        # Create demo output file with enhanced formatting
        output_path = Path(self.output_dir) / output_file
        demo_content = f"""{'=' * 80}
ipsnipe Scan Report - {description} (DEMO MODE)
{'=' * 80}

Command: {' '.join(command)}
Target: {self.target_ip}
Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
End Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Execution Time: 2.34 seconds
Return Code: 0
Status: SUCCESS

{'=' * 80}

SCAN RESULTS:
----------------------------------------
[DEMO MODE] This is simulated output for: {description}

Sample results would appear here in a real scan:
🔓 22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
🔓 80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
🔓 443/tcp  open  https   Apache httpd 2.4.41 ((Ubuntu))
🔓 3306/tcp open  mysql   MySQL 8.0.32-0ubuntu0.20.04.2
🔓 161/udp  open  snmp    SNMPv1 server (for UDP scans)
📁 /admin          (Status: 200) [Size: 1234] (for Gobuster/Feroxbuster/ffuf)
📁 /login          (Status: 200) [Size: 856] (for directory enumeration)
↪️  /dashboard      (Status: 302) [Size: 0] -> /login (for redirects)
🔒 /config         (Status: 403) [Size: 277] (for forbidden directories)
⚠️  OSVDB-3092: /admin/: This might be interesting... (for Nikto)
⚠️  CVE-2021-41773: Apache 2.4.49-2.4.50 mod_cgi path traversal
ℹ️  Server: Apache/2.4.41 (Ubuntu)
🔧 Apache/2.4.41 (Ubuntu) (for WhatWeb)
🔧 MySQL (for technology detection)
🔧 PHP/7.4.3 (for web frameworks)
📧 admin@htb.local (for theHarvester)
📧 support@htb.local (for email enumeration)
🌐 api.htb.local (for subdomain discovery)
🔍 A record: htb.local -> 10.10.10.123 (for DNSrecon)
🔍 MX record: htb.local -> mail.htb.local (for DNS records)

This demo shows the interface without running actual scans.
The real ipsnipe would show actual findings with emoji highlights for easy analysis.

NEW FEATURES IN THIS VERSION:
- 🔌 Custom port ranges (1-1000, 80,443,8080, etc.)
- 🧠 Smart web service detection and automatic skipping
- 🎯 Port-specific targeting for web enumeration
- ⏭️  Intelligent scan optimization

{'=' * 80}
End of {description} Report (DEMO)
{'=' * 80}
"""
        
        with open(output_path, 'w') as f:
            f.write(demo_content)
        
        file_size = len(demo_content.encode('utf-8'))
        print(f"{Colors.GREEN}✅ {description} completed successfully (2.3s, {file_size} bytes) [DEMO]{Colors.END}")
        return {
            'status': 'success',
            'output_file': str(output_path),
            'execution_time': 2.34,
            'file_size': file_size,
            'return_code': 0
        }
    
    def run_attacks(self, selected_attacks, port_range=None):
        """Demo version of run_attacks with enhanced features"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Starting reconnaissance on {self.target_ip}... [DEMO]{Colors.END}\n")
        
        # Simulate port range selection
        if any(scan in selected_attacks for scan in ['nmap_quick', 'nmap_full', 'nmap_udp']) and not port_range:
            port_range = self.get_port_range_input()
        
        # Execute all selected scans with enhanced status reporting
        for attack in selected_attacks:
            if attack == 'nmap_quick':
                self.results[attack] = self.nmap_quick_scan(port_range)
            elif attack == 'nmap_full':
                self.results[attack] = self.nmap_full_scan(port_range)
            elif attack == 'nmap_udp':
                self.results[attack] = self.nmap_udp_scan(port_range)
            elif attack in ['gobuster_common', 'gobuster_big', 'feroxbuster', 'ffuf', 'nikto', 'whatweb']:
                # Demonstrate smart web detection
                if self.should_run_web_scan(attack):
                    if attack == 'gobuster_common':
                        self.results[attack] = self.gobuster_common()
                    elif attack == 'gobuster_big':
                        self.results[attack] = self.gobuster_big()
                    elif attack == 'feroxbuster':
                        self.results[attack] = self.feroxbuster_scan()
                    elif attack == 'ffuf':
                        self.results[attack] = self.ffuf_scan()
                    elif attack == 'nikto':
                        self.results[attack] = self.nikto_scan()
                    elif attack == 'whatweb':
                        self.results[attack] = self.whatweb_scan()
                else:
                    # Simulate skipped scan
                    self.results[attack] = {'status': 'skipped', 'reason': 'No web services detected'}
                    print(f"{Colors.YELLOW}⏭️  {attack.replace('_', ' ').title()} - No web services detected [DEMO]{Colors.END}")
            elif attack == 'theharvester':
                self.results[attack] = self.theharvester_scan()
            elif attack == 'dnsrecon':
                self.results[attack] = self.dnsrecon_scan()
            
            # Show results status
            if attack in self.results:
                status = self.results[attack]['status']
                if status == 'skipped':
                    print(f"{Colors.YELLOW}⏭️  {attack.replace('_', ' ').title()} - {self.results[attack].get('reason', 'Skipped')} [DEMO]{Colors.END}")
                elif status == 'success':
                    print(f"{Colors.GREEN}✅ {attack.replace('_', ' ').title()} - Completed [DEMO]{Colors.END}")
            
            print()  # Add spacing between attacks
        
        self.generate_summary_report()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All scans completed! [DEMO]{Colors.END}")
        print(f"{Colors.CYAN}📁 Results saved in: {self.output_dir}{Colors.END}")
        print(f"{Colors.CYAN}📋 Check SUMMARY_REPORT.md for an overview{Colors.END}")
        
        # Show web service detection summary
        if hasattr(self, 'demo_web_ports') and self.demo_web_ports:
            print(f"{Colors.GREEN}🌐 Web services detected on ports: {sorted(self.demo_web_ports)} [DEMO]{Colors.END}")
        
        print(f"{Colors.CYAN}💡 Tip: Review individual scan files for detailed results{Colors.END}")
        
        # Show demo-specific information
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🎭 Demo Summary:{Colors.END}")
        print(f"{Colors.YELLOW}  📊 This demo showcased all new features:{Colors.END}")
        print(f"{Colors.GREEN}    ✅ Port range validation and input{Colors.END}")
        print(f"{Colors.GREEN}    ✅ Smart web service detection{Colors.END}")
        print(f"{Colors.GREEN}    ✅ Intelligent scan skipping{Colors.END}")
        print(f"{Colors.GREEN}    ✅ Enhanced status reporting{Colors.END}")
        print(f"{Colors.GREEN}    ✅ Port-specific targeting{Colors.END}")
        print(f"{Colors.CYAN}  📝 Real scans would show actual security findings{Colors.END}")
    
    def check_dependencies(self):
        """Demo version that shows what dependency checking looks like"""
        tools = ['nmap', 'gobuster', 'nikto', 'whatweb', 'feroxbuster', 'ffuf', 'theHarvester', 'dnsrecon']
        
        print(f"{Colors.YELLOW}🔍 Checking dependencies...{Colors.END}")
        
        for tool in tools:
            time.sleep(0.3)  # Simulate checking
            print(f"{Colors.GREEN}✅ {tool} found (DEMO){Colors.END}")
        
        print(f"{Colors.GREEN}✅ All dependencies found! (DEMO MODE){Colors.END}")
        return True
    
    def get_port_range_input(self) -> str:
        """Demo version of port range input with automatic selection"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔌 Port Range Configuration: [DEMO]{Colors.END}")
        print(f"{Colors.YELLOW}Examples:{Colors.END}")
        print(f"  • {Colors.CYAN}80{Colors.END} - Single port")
        print(f"  • {Colors.CYAN}1-1000{Colors.END} - Port range")
        print(f"  • {Colors.CYAN}80,443,8080{Colors.END} - Specific ports")
        print(f"  • {Colors.CYAN}1-65535{Colors.END} - All ports")
        print(f"  • {Colors.GREEN}default{Colors.END} - Use default configuration")
        
        # Simulate user input for demo
        demo_range = "1-1000"
        print(f"\n{Colors.CYAN}🎯 Enter port range (or 'default'): {Colors.END}{Colors.YELLOW}{demo_range} [AUTO-SELECTED]{Colors.END}")
        time.sleep(1)
        print(f"{Colors.GREEN}✅ Valid port range: {demo_range}{Colors.END}")
        return demo_range
    
    def should_run_web_scan(self, scan_type: str) -> bool:
        """Demo version that shows web detection logic"""
        web_scan_types = ['gobuster_common', 'gobuster_big', 'feroxbuster', 'ffuf', 'nikto', 'whatweb']
        
        if scan_type not in web_scan_types:
            return True  # Always run non-web scans
        
        # Simulate having detected web services in demo
        if hasattr(self, 'demo_web_ports') and self.demo_web_ports:
            print(f"{Colors.GREEN}🌐 Web services detected on ports: {sorted(self.demo_web_ports)} - Running {scan_type.replace('_', ' ').title()} [DEMO]{Colors.END}")
            return True
        else:
            print(f"{Colors.YELLOW}⏭️  Skipping {scan_type.replace('_', ' ').title()} - No web services found [DEMO]{Colors.END}")
            return False
    
    def demonstrate_port_validation(self):
        """Demonstrate the port range validation feature"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🧪 Port Range Validation Demo:{Colors.END}")
        
        test_cases = [
            ('80', True, 'Single port'),
            ('1-1000', True, 'Port range'),
            ('80,443,8080', True, 'Specific ports'),
            ('default', True, 'Default keyword'),
            ('0', False, 'Invalid port (too low)'),
            ('65536', False, 'Invalid port (too high)'),
            ('abc', False, 'Invalid format'),
        ]
        
        for port_range, expected, description in test_cases:
            result = self.validate_port_range(port_range)
            status = "✅ VALID" if result else "❌ INVALID"
            color = Colors.GREEN if result else Colors.RED
            print(f"  {color}{status}{Colors.END} '{port_range}' - {description}")
            time.sleep(0.3)
    
    def demonstrate_web_detection(self):
        """Demonstrate smart web service detection"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🧠 Smart Web Detection Demo:{Colors.END}")
        print(f"{Colors.CYAN}  📡 Parsing Nmap output for open ports...{Colors.END}")
        time.sleep(0.5)
        print(f"{Colors.GREEN}  🔓 Found open ports: {self.demo_open_ports}{Colors.END}")
        time.sleep(0.5)
        print(f"{Colors.CYAN}  🔍 Analyzing services for web components...{Colors.END}")
        time.sleep(0.5)
        print(f"{Colors.GREEN}  🌐 Detected web services on: {self.demo_web_ports}{Colors.END}")
        time.sleep(0.5)
        print(f"{Colors.YELLOW}  🎯 Web scans will target these specific ports{Colors.END}")
        time.sleep(0.5)
        print(f"{Colors.BLUE}  ⏭️  Non-web scans would be skipped if no web services found{Colors.END}")
    
    def show_disclaimer(self):
        """Display demo disclaimer (simplified for demo mode)"""
        print(f"{Colors.YELLOW}🎭 DEMO MODE DISCLAIMER{Colors.END}")
        print(f"{Colors.CYAN}This is a demonstration of ipsnipe's interface.{Colors.END}")
        print(f"{Colors.CYAN}No actual scans will be performed.{Colors.END}")
        print(f"{Colors.WHITE}Remember: Always use security tools ethically and legally!{Colors.END}\n")

    def print_banner(self):
        """Display the demo banner"""
        print(f"{Colors.CYAN}{BANNER}{Colors.END}")
        print(f"{Colors.YELLOW}Welcome to ipsnipe - Your Advanced Reconnaissance Framework!{Colors.END}")
        print(f"{Colors.BLUE}Created by hckerhub | {Colors.CYAN}https://hackerhub.me{Colors.END}")
        print(f"{Colors.PURPLE}Support the project: {Colors.YELLOW}https://buymeacoffee.com/hckerhub{Colors.END}")
        print(f"{Colors.RED}🎭 DEMO MODE - No actual scans will be performed{Colors.END}\n")

def main():
    """Demo main function"""
    print(f"{Colors.BLUE}🎭 ipsnipe Demo Mode{Colors.END}")
    print(f"{Colors.YELLOW}This demo shows ipsnipe's interface without running actual scans{Colors.END}")
    print(f"{Colors.CYAN}Perfect for testing the tool or showing its capabilities{Colors.END}\n")
    
    # Show what's new in this version
    print(f"{Colors.BOLD}{Colors.PURPLE}🆕 NEW FEATURES IN THIS VERSION:{Colors.END}")
    print(f"{Colors.GREEN}  🔌 Custom Port Ranges - Flexible port selection{Colors.END}")
    print(f"{Colors.GREEN}  🧠 Smart Web Detection - Automatic service detection{Colors.END}")
    print(f"{Colors.GREEN}  🎯 Port-Specific Targeting - Uses discovered ports{Colors.END}")
    print(f"{Colors.GREEN}  ⏭️  Intelligent Skipping - Skips irrelevant scans{Colors.END}")
    
    try:
        demo = ipsnipdemo()
        
        # Demonstrate new features before running main demo
        demo.demonstrate_port_validation()
        demo.demonstrate_web_detection()
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}🚀 Starting Full Interface Demo:{Colors.END}")
        time.sleep(2)
        
        demo.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Demo interrupted by user. Goodbye!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {str(e)}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main() 