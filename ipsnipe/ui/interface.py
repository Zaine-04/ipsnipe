#!/usr/bin/env python3
"""
User interface functionality for ipsnipe
Handles menus, user input, disclaimers, and interactions
"""

import subprocess
import os
from typing import List
from pathlib import Path
from .colors import Colors, print_banner
from .validators import Validators


class UserInterface:
    """User interface and interaction handling"""
    
    def __init__(self):
        pass
    
    def show_disclaimer(self):
        """Show ethical use disclaimer"""
        disclaimer = f"""
{Colors.BOLD}{Colors.RED}⚠️  ETHICAL USE DISCLAIMER ⚠️{Colors.END}

{Colors.YELLOW}ipsnipe is a reconnaissance tool designed for ethical hacking, 
penetration testing, and security research purposes ONLY.{Colors.END}

{Colors.BOLD}YOU MUST:{Colors.END}
✅ Only use this tool on systems you own or have explicit written permission to test
✅ Comply with all applicable local, state, and federal laws
✅ Respect the privacy and rights of others
✅ Use findings responsibly and report vulnerabilities appropriately

{Colors.BOLD}YOU MUST NOT:{Colors.END}
❌ Use this tool for illegal activities or unauthorized access
❌ Test systems without proper authorization
❌ Cause damage to systems or networks
❌ Violate terms of service or acceptable use policies

{Colors.RED}The developers of ipsnipe are not responsible for any misuse 
of this tool or any damages caused by its use.{Colors.END}

{Colors.CYAN}By using ipsnipe, you acknowledge that you understand and agree 
to use this tool in a legal and ethical manner only.{Colors.END}
        """
        
        print(disclaimer)
        
        while True:
            response = input(f"\n{Colors.BOLD}Do you agree to use ipsnipe ethically and legally? (yes/no): {Colors.END}").strip().lower()
            if response in ['yes', 'y']:
                print(f"{Colors.GREEN}✅ Thank you for your commitment to ethical use!{Colors.END}\n")
                break
            elif response in ['no', 'n']:
                print(f"{Colors.RED}❌ You must agree to ethical use to continue. Exiting...{Colors.END}")
                exit(1)
            else:
                print(f"{Colors.YELLOW}Please answer 'yes' or 'no'{Colors.END}")
    
    def check_root_privileges(self) -> bool:
        """Check if running with root privileges"""
        return os.geteuid() == 0
    
    def test_sudo_access(self) -> bool:
        """Test if user has sudo access"""
        try:
            subprocess.run(['sudo', '-n', 'true'], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_sudo_mode_preference(self, force_mode=None) -> bool:
        """Get user preference for Enhanced Mode (sudo)"""
        if force_mode is not None:
            return force_mode
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔐 ipsnipe Enhanced Mode Selection{Colors.END}")
        print(f"{Colors.CYAN}════════════════════════════════════{Colors.END}\n")
        
        is_root = self.check_root_privileges()
        has_sudo = self.test_sudo_access()
        
        if is_root:
            print(f"{Colors.GREEN}✅ Running as root - Enhanced Mode automatically enabled{Colors.END}")
            print(f"{Colors.CYAN}Features: SYN scans, OS detection, UDP scans{Colors.END}")
            return True
        
        if has_sudo:
            print(f"{Colors.GREEN}✅ Sudo access detected{Colors.END}")
            print(f"\n{Colors.BOLD}Choose scan mode:{Colors.END}")
            print(f"  {Colors.GREEN}1) Enhanced Mode (sudo){Colors.END} - SYN scans, OS detection, UDP scans")
            print(f"  {Colors.YELLOW}2) Standard Mode{Colors.END} - TCP connect scans only")
            
            while True:
                choice = input(f"\n{Colors.CYAN}Select mode (1-2, default: 1): {Colors.END}").strip()
                
                if choice in ['1', ''] or choice.lower() in ['enhanced', 'e']:
                    print(f"{Colors.GREEN}✅ Enhanced Mode selected - Using sudo for advanced scanning{Colors.END}")
                    return True
                elif choice in ['2'] or choice.lower() in ['standard', 's']:
                    print(f"{Colors.YELLOW}⚡ Standard Mode selected - Basic TCP scanning{Colors.END}")
                    return False
                else:
                    print(f"{Colors.RED}Invalid choice. Please select 1 or 2.{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  No sudo access detected{Colors.END}")
            print(f"{Colors.CYAN}Running in Standard Mode - TCP connect scans only{Colors.END}")
            print(f"{Colors.CYAN}💡 For Enhanced Mode features, ensure sudo access is available{Colors.END}")
            return False
    
    def get_target_ip(self) -> str:
        """Get and validate target IP address"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🎯 Target Selection{Colors.END}")
        print(f"{Colors.CYAN}═══════════════════{Colors.END}")
        
        while True:
            ip = input(f"\n{Colors.CYAN}Enter target IP address: {Colors.END}").strip()
            
            if not ip:
                print(f"{Colors.RED}Please enter an IP address{Colors.END}")
                continue
            
            if Validators.validate_ip(ip):
                print(f"{Colors.GREEN}✅ Valid IP address: {ip}{Colors.END}")
                return ip
            else:
                print(f"{Colors.RED}❌ Invalid IP address format. Please try again.{Colors.END}")
                print(f"{Colors.CYAN}💡 Example: 192.168.1.1{Colors.END}")
    
    def get_port_range_input(self) -> str:
        """Get port range input from user"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔌 Port Range Selection{Colors.END}")
        print(f"{Colors.CYAN}═══════════════════════════{Colors.END}")
        
        print(f"\n{Colors.BOLD}Port range options:{Colors.END}")
        print(f"  📋 {Colors.GREEN}default{Colors.END} - Use tool defaults (recommended)")
        print(f"  🔢 {Colors.YELLOW}1-1000{Colors.END} - Scan ports 1 to 1000")
        print(f"  🎯 {Colors.YELLOW}80,443,8080{Colors.END} - Scan specific ports")
        print(f"  🌐 {Colors.YELLOW}80-443{Colors.END} - Scan port range")
        print(f"  📡 {Colors.CYAN}1-65535{Colors.END} - Full port scan (slow)")
        
        while True:
            port_range = input(f"\n{Colors.CYAN}Enter port range (default: default): {Colors.END}").strip()
            
            if not port_range or port_range.lower() == 'default':
                print(f"{Colors.GREEN}✅ Using default port ranges{Colors.END}")
                return 'default'
            
            if Validators.validate_port_range(port_range):
                normalized = Validators.normalize_port_range(port_range)
                print(f"{Colors.GREEN}✅ Valid port range: {normalized}{Colors.END}")
                
                # Show warning for large ranges
                ports = Validators.expand_port_range(normalized)
                if len(ports) > 1000:
                    print(f"{Colors.YELLOW}⚠️  Large port range ({len(ports)} ports) - scan may take a while{Colors.END}")
                
                return normalized
            else:
                print(f"{Colors.RED}❌ Invalid port range format{Colors.END}")
                print(f"{Colors.CYAN}💡 Valid formats: 80, 80-443, 80,443,8080{Colors.END}")
    
    def create_output_directory(self, ip: str) -> str:
        """Create output directory for scan results"""
        timestamp = Path(f"ipsnipe_scan_{ip}_{Path.cwd().name}")
        output_dir = Path.cwd() / timestamp.name
        
        # Create unique directory if it already exists
        counter = 1
        while output_dir.exists():
            output_dir = Path.cwd() / f"{timestamp.name}_{counter}"
            counter += 1
        
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}📁 Created output directory: {output_dir}{Colors.END}")
        return str(output_dir)
    
    def show_attack_menu(self) -> List[str]:
        """Display attack selection menu and return selected attacks"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🛡️  ipsnipe Reconnaissance Suite{Colors.END}")
        print(f"{Colors.CYAN}═══════════════════════════════════════{Colors.END}")
        
        attacks = {
            '1': ('nmap_quick', '🔍 Nmap Quick Scan', 'Fast port discovery and service detection'),
            '2': ('nmap_full', '🔎 Nmap Full Scan', 'Comprehensive port scan with scripts'),
            '3': ('nmap_udp', '📡 Nmap UDP Scan', 'UDP port discovery (requires sudo)'),
            '4': ('web_detect', '🌐 Web Service Detection', 'Direct HTTP/HTTPS service detection'),
            '5': ('gobuster_common', '📁 Gobuster Common', 'Web directory enumeration (common wordlist)'),
            '6': ('gobuster_big', '📂 Gobuster Big', 'Web directory enumeration (large wordlist)'),
            '7': ('feroxbuster', '🦀 Feroxbuster', 'Fast recursive web content discovery'),
            '8': ('ffuf', '💨 FFUF', 'Fast web fuzzer for content discovery'),
            '9': ('nikto', '🔬 Nikto', 'Web vulnerability scanner'),
            '10': ('whatweb', '🕸️  WhatWeb', 'Web technology fingerprinting'),
            '11': ('theharvester', '📧 theHarvester', 'Email and subdomain enumeration'),
            '12': ('dnsrecon', '🌐 DNSRecon', 'DNS enumeration and reconnaissance')
        }
        
        print(f"\n{Colors.BOLD}Available reconnaissance modules:{Colors.END}")
        for key, (_, name, desc) in attacks.items():
            print(f"  {Colors.YELLOW}{key.rjust(2)}) {name}{Colors.END} - {desc}")
        
        print(f"\n{Colors.PURPLE}💡 New Feature: Interruptible Scans{Colors.END}")
        print(f"{Colors.CYAN}   • During scans, press 's' + Enter to skip current scan{Colors.END}")
        print(f"{Colors.CYAN}   • Press 'q' + Enter to quit all remaining scans{Colors.END}")
        print(f"{Colors.CYAN}   • Use Ctrl+C for emergency termination{Colors.END}")
        
        print(f"\n{Colors.BOLD}Quick selections:{Colors.END}")
        print(f"  {Colors.GREEN}🚀 all{Colors.END} - Run all available modules")
        print(f"  {Colors.BLUE}🌐 web{Colors.END} - Run all web-related scans (5-10)")
        print(f"  {Colors.PURPLE}🔍 nmap{Colors.END} - Run all Nmap scans (1-3)")
        print(f"  {Colors.CYAN}🎯 basic{Colors.END} - Run essential scans (1,4,9,10)")
        
        while True:
            selection = input(f"\n{Colors.CYAN}Select modules (comma-separated, e.g., 1,2,4 or 'all'): {Colors.END}").strip()
            
            if not selection:
                print(f"{Colors.RED}Please make a selection{Colors.END}")
                continue
            
            try:
                selected_attacks = []
                
                if selection.lower() == 'all':
                    selected_attacks = [attack for attack, _, _ in attacks.values()]
                elif selection.lower() == 'web':
                    selected_attacks = ['gobuster_common', 'gobuster_big', 'feroxbuster', 'ffuf', 'nikto', 'whatweb']
                elif selection.lower() == 'nmap':
                    selected_attacks = ['nmap_quick', 'nmap_full', 'nmap_udp']
                elif selection.lower() == 'basic':
                    selected_attacks = ['nmap_quick', 'web_detect', 'nikto', 'whatweb']
                else:
                    # Parse individual selections
                    choices = [choice.strip() for choice in selection.split(',')]
                    for choice in choices:
                        if choice in attacks:
                            attack_name = attacks[choice][0]
                            if attack_name not in selected_attacks:
                                selected_attacks.append(attack_name)
                        else:
                            print(f"{Colors.RED}Invalid selection: {choice}{Colors.END}")
                            raise ValueError("Invalid selection")
                
                if selected_attacks:
                    print(f"\n{Colors.GREEN}✅ Selected {len(selected_attacks)} module(s):{Colors.END}")
                    for attack in selected_attacks:
                        attack_info = next((info for key, info in attacks.items() if info[0] == attack), None)
                        if attack_info:
                            print(f"  • {attack_info[1]}")
                    return selected_attacks
                else:
                    print(f"{Colors.RED}No valid modules selected{Colors.END}")
                    
            except ValueError:
                print(f"{Colors.RED}Invalid selection format. Please try again.{Colors.END}")
                print(f"{Colors.CYAN}💡 Use numbers (1,2,3), 'all', 'web', or 'nmap'{Colors.END}")
    
    def show_scan_summary(self, target_ip: str, output_dir: str, enhanced_mode: bool, selected_attacks: List[str]) -> bool:
        """Show scan configuration summary and get confirmation"""
        print(f"\n{Colors.BOLD}📋 Scan Configuration Summary:{Colors.END}")
        print(f"  🎯 Target IP: {Colors.CYAN}{target_ip}{Colors.END}")
        print(f"  📁 Output Directory: {Colors.CYAN}{output_dir}{Colors.END}")
        print(f"  🔐 Enhanced Mode: {'✅ Enabled (sudo)' if enhanced_mode else '❌ Disabled (standard)'}")
        print(f"\n{Colors.BOLD}📋 Selected modules ({len(selected_attacks)}):{Colors.END}")
        
        for attack in selected_attacks:
            enhanced_note = ""
            if attack in ['nmap_quick', 'nmap_full'] and enhanced_mode:
                enhanced_note = " (SYN scan + OS detection)"
            elif attack == 'nmap_udp' and not enhanced_mode:
                enhanced_note = " (will be skipped - requires sudo)"
            elif attack == 'nmap_udp' and enhanced_mode:
                enhanced_note = " (UDP scan enabled)"
            print(f"  • {attack.replace('_', ' ').title()}{enhanced_note}")
        
        confirm = input(f"\n{Colors.CYAN}🚀 Start reconnaissance? (y/N): {Colors.END}").strip().lower()
        return confirm in ['y', 'yes'] 