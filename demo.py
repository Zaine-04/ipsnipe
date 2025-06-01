#!/usr/bin/env python3
"""
BoxRecon Demo Script
Shows the interface and functionality without running actual scans
"""

import time
import sys
import datetime
from pathlib import Path

# Import BoxRecon classes
from boxrecon import BoxRecon, Colors, BANNER

class BoxReconDemo(BoxRecon):
    """Demo version of BoxRecon that simulates scans without running actual commands"""
    
    def __init__(self):
        super().__init__()
        self.demo_mode = True
    
    def run_command(self, command, output_file, description, scan_type="generic"):
        """Simulate command execution for demo purposes"""
        timeout = self.config['general']['scan_timeout']
        print(f"{Colors.YELLOW}🔄 Running: {description}... (timeout: {timeout}s) [DEMO]{Colors.END}")
        
        # Simulate execution time
        for i in range(3):
            print(f"{Colors.BLUE}   {'.' * (i + 1)}{Colors.END}")
            time.sleep(0.5)
        
        # Create demo output file with enhanced formatting
        output_path = Path(self.output_dir) / output_file
        demo_content = f"""{'=' * 80}
BoxRecon Scan Report - {description} (DEMO MODE)
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
🔓 22/tcp   open  ssh     OpenSSH 8.2p1 (for Nmap TCP)
🔓 161/udp  open  snmp    (for Nmap UDP)
📁 /admin   (Status: 200) [Size: 1234] (for Gobuster/Feroxbuster/ffuf)
⚠️  OSVDB-3092: /admin/: This might be interesting... (for Nikto)
🔧 Apache/2.4.41 (Ubuntu) (for WhatWeb)
📧 admin@example.com (for theHarvester)
🔍 A record: example.com -> 10.10.10.123 (for DNSrecon)

This demo shows the interface without running actual scans.
The real BoxRecon would show actual findings with emoji highlights.

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
    
    def check_dependencies(self):
        """Demo version that shows what dependency checking looks like"""
        tools = ['nmap', 'gobuster', 'nikto', 'whatweb', 'feroxbuster', 'ffuf', 'theHarvester', 'dnsrecon']
        
        print(f"{Colors.YELLOW}🔍 Checking dependencies...{Colors.END}")
        
        for tool in tools:
            time.sleep(0.3)  # Simulate checking
            print(f"{Colors.GREEN}✅ {tool} found (DEMO){Colors.END}")
        
        print(f"{Colors.GREEN}✅ All dependencies found! (DEMO MODE){Colors.END}")
        return True
    
    def show_disclaimer(self):
        """Display demo disclaimer (simplified for demo mode)"""
        print(f"{Colors.YELLOW}🎭 DEMO MODE DISCLAIMER{Colors.END}")
        print(f"{Colors.CYAN}This is a demonstration of BoxRecon's interface.{Colors.END}")
        print(f"{Colors.CYAN}No actual scans will be performed.{Colors.END}")
        print(f"{Colors.WHITE}Remember: Always use security tools ethically and legally!{Colors.END}\n")

    def print_banner(self):
        """Display the demo banner"""
        print(f"{Colors.CYAN}{BANNER}{Colors.END}")
        print(f"{Colors.YELLOW}Welcome to BoxRecon - Your Advanced Reconnaissance Framework!{Colors.END}")
        print(f"{Colors.BLUE}Created by hckerhub | {Colors.CYAN}https://hackerhub.me{Colors.END}")
        print(f"{Colors.PURPLE}Support the project: {Colors.YELLOW}https://buymeacoffee.com/hckerhub{Colors.END}")
        print(f"{Colors.RED}🎭 DEMO MODE - No actual scans will be performed{Colors.END}\n")

def main():
    """Demo main function"""
    print(f"{Colors.BLUE}🎭 BoxRecon Demo Mode{Colors.END}")
    print(f"{Colors.YELLOW}This demo shows BoxRecon's interface without running actual scans{Colors.END}")
    print(f"{Colors.CYAN}Perfect for testing the tool or showing its capabilities{Colors.END}\n")
    
    try:
        demo = BoxReconDemo()
        demo.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Demo interrupted by user. Goodbye!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {str(e)}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main() 