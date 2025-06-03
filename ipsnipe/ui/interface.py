#!/usr/bin/env python3
"""
Rich-powered user interface for ipsnipe
Simplified menus, prompts, and interactions
"""

import subprocess
import os
from typing import List
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from .colors import print_banner, console
from .validators import Validators


class UserInterface:
    """Rich-powered user interface and interaction handling"""
    
    def __init__(self):
        self.console = console
    
    def show_disclaimer(self):
        """Show simplified ethical use disclaimer"""
        self.console.print("\n⚠️  ETHICAL USE ONLY ⚠️", style="bold red")
        self.console.print("This tool is for authorized testing only.", style="yellow")
        self.console.print("Only scan systems you own or have permission to test.", style="cyan")
        
        if not Confirm.ask("\nAgree to ethical use?"):
            self.console.print("❌ Exiting...", style="red")
            exit(1)
        
        self.console.print("✅ Ethical use acknowledged", style="green")
    
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
        """Get user preference for Enhanced Mode (sudo) - simplified"""
        if force_mode is not None:
            return force_mode
        
        self.console.print("\n🔐 Scan Mode", style="bold cyan")
        
        is_root = self.check_root_privileges()
        if is_root:
            self.console.print("✅ Running as root - Enhanced mode enabled", style="green")
            return True
        
        has_sudo = self.test_sudo_access()
        
                # Simplified explanation
        self.console.print("\nEnhanced mode enables faster, more comprehensive scans", style="cyan")
        if not has_sudo:
            self.console.print("⚠️  May require password", style="yellow")
        
        # Display creator attribution message
        self.console.print("\nHappy ethical hacking! 🎯\n", style="bright_green")
        self.console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", style="cyan")
        self.console.print("ipsnipe created by hckerhub, thank you for trying my tool! ❤️", style="bold white")
        self.console.print("🌐 Website: https://hackerhub.me", style="blue")
        self.console.print("🐦 X: @hckerhub", style="blue")
        self.console.print("☕ Support: https://buymeacoffee.com/hckerhub", style="yellow")
        self.console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", style="cyan")
        
        if Confirm.ask("\nUse enhanced mode?", default=True):
            self.console.print("✅ Enhanced mode enabled", style="green")
            return True
        else:
            self.console.print("⚡ Standard mode selected", style="yellow")
            return False
    
    def get_target_ip(self) -> str:
        """Get and validate target IP address - simplified"""
        self.console.print("\n🎯 Target", style="bold cyan")
        
        while True:
            ip = Prompt.ask("IP address").strip()
            
            if not ip:
                self.console.print("Please enter an IP address", style="red")
                continue
            
            if Validators.validate_ip(ip):
                self.console.print(f"✅ Target set: {ip}", style="green")
                return ip
            else:
                self.console.print("❌ Invalid format (example: 192.168.1.1)", style="red")
    
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
        self.console.print(f"📁 Output: {output_dir.name}", style="green")
        return str(output_dir)
    
    def show_attack_menu(self) -> List[str]:
        """Show Full Sniper Mode explanation and workflow"""
        # Create a beautiful panel for the title
        title_panel = Panel(
            "[red]🎯 Full Sniper Mode[/red]\n[cyan]Complete reconnaissance suite with intelligent workflow[/cyan]\n[yellow]📢 Other scan modes coming soon![/yellow]",
            border_style="bright_blue"
        )
        self.console.print(title_panel)
        
        # Create workflow table
        workflow_table = Table(title="🔄 Three-Phase Workflow", show_header=True, header_style="bold magenta")
        workflow_table.add_column("Phase", style="cyan", width=6)
        workflow_table.add_column("Name", style="green", width=20)
        workflow_table.add_column("Description", style="white")
        
        workflow_table.add_row("1", "Network Discovery", "Port scanning & service detection")
        workflow_table.add_row("2", "Domain Intelligence", "DNS enumeration & domain discovery")
        workflow_table.add_row("3", "Web Analysis", "Content discovery & vulnerability testing")
        
        self.console.print(workflow_table)
        
        # Tools info
        self.console.print("\n🛠️  10 Integrated Tools:", style="bold")
        self.console.print("  🔎 Network Scan • 📡 UDP Scan • 🌐 DNS Enum • 🚀 Advanced DNS")
        self.console.print("  📧 Email Harvest • 🌐 Web Discovery • 🦀 Directory Scan")
        self.console.print("  💨 Subdomain Fuzz • 🏗️ CMS Detection • 🎯 Parameter Test")
        
        # Smart features
        self.console.print("\n💡 Smart Features:", style="cyan")
        self.console.print("  • Automatic domain discovery & /etc/hosts management")
        self.console.print("  • Intelligent tool chaining (results feed next tools)")
        self.console.print("  • Real-time controls: 's' to skip, 'q' to quit")
        
        self.console.print("\n⏱️  Estimated time: 30-60 minutes", style="yellow")
        
        if Confirm.ask("\nExecute Full Sniper Mode?", default=True):
            self.console.print("✅ Full Sniper Mode activated", style="green")
            # Return all tools for Full Sniper Mode
            return ['nmap_full', 'nmap_udp', 'dns_enumeration', 'advanced_dns', 
                   'theharvester', 'enhanced_web', 'feroxbuster', 'ffuf', 
                   'cms_scan', 'param_lfi_scan']
        else:
            self.console.print("👋 Reconnaissance cancelled.", style="yellow")
            exit(0)
    
    def show_scan_summary(self, target_ip: str, output_dir: str, enhanced_mode: bool, selected_attacks: List[str]) -> bool:
        """Show Full Sniper Mode scan summary"""
        # Create summary table
        summary_table = Table(title="📋 Full Sniper Mode Summary", show_header=True, header_style="bold cyan")
        summary_table.add_column("Setting", style="cyan", width=12)
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("🎯 Target", target_ip)
        summary_table.add_row("📁 Output", Path(output_dir).name)
        summary_table.add_row("🔐 Mode", "Enhanced" if enhanced_mode else "Standard")
        summary_table.add_row("🛠️  Tools", f"{len(selected_attacks)} reconnaissance modules")
        summary_table.add_row("📊 Type", "[red]Full Sniper Mode[/red]")
        
        self.console.print(summary_table)
        
        if Confirm.ask("\nStart Full Sniper Mode?", default=True):
            self.console.print("🚀 Starting Full Sniper Mode...", style="green")
            return True
        else:
            return False 