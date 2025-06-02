#!/usr/bin/env python3
"""
ipsnipe Uninstall Script
This script will help you remove ipsnipe and its dependencies safely.
"""

import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class IPSnipeUninstaller:
    def __init__(self):
        self.os_type = self.detect_os()
        self.installed_python_packages = []
        self.installed_system_tools = []
        self.project_files = []
        self.keep_packages = []
        self.keep_tools = []
        
        # Define packages and tools that ipsnipe uses
        self.python_packages = ['toml', 'colorama', 'rich']
        self.system_tools = {
            'nmap': 'nmap',
            
            'feroxbuster': 'feroxbuster',
            'ffuf': 'ffuf',
            'theHarvester': 'theHarvester',
            'whatweb': 'whatweb',
            'ruby': 'ruby'
        }
        
    def detect_os(self):
        """Detect the operating system"""
        system = platform.system().lower()
        if system == 'linux':
            if shutil.which('apt'):
                return 'debian'
            elif shutil.which('pacman'):
                return 'arch'
            else:
                return 'linux'
        elif system == 'darwin':
            return 'macos'
        else:
            return 'unknown'
    
    def print_banner(self):
        """Print the uninstall banner"""
        print(f"{Colors.RED}")
        print("""
 ___  ________  ________  ________   ___  ________  _______      
|\  \|\   __  \|\   ____\|\   ___  \|\  \|\   __  \|\  ___ \     
\ \  \ \  \|\  \ \  \___|\ \  \\ \  \ \  \ \  \|\  \ \   __/|    
 \ \  \ \   ____\ \_____  \ \  \\ \  \ \  \ \   ____\ \  \_|/__  
  \ \  \ \  \___|\|____|\  \ \  \\ \  \ \  \ \  \___|\ \  \_|\ \ 
   \ \__\ \__\     ____\_\  \ \__\\ \__\ \__\ \__\    \ \_______\\
    \|__|\|__|    |\_________\|__| \|__|\|__|\|__|     \|_______|
                  \|_________|                                   

        🗑️  ipsnipe Uninstall Script 🗑️
        ═══════════════════════════════════
        """)
        print(f"{Colors.NC}")
    
    def check_command(self, command):
        """Check if a command exists"""
        return shutil.which(command) is not None
    
    def check_python_package(self, package):
        """Check if a Python package is installed"""
        try:
            result = subprocess.run([sys.executable, '-c', f'import {package}'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def scan_installed_dependencies(self):
        """Scan for installed dependencies"""
        print(f"{Colors.YELLOW}🔍 Scanning for installed dependencies...{Colors.NC}\n")
        
        # Check Python packages
        print(f"{Colors.CYAN}🐍 Python Packages:{Colors.NC}")
        for package in self.python_packages:
            if self.check_python_package(package):
                self.installed_python_packages.append(package)
                print(f"{Colors.GREEN}✅ {package} - INSTALLED{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}⚪ {package} - not installed{Colors.NC}")
        
        # Check system tools
        print(f"\n{Colors.CYAN}🛠️  System Tools:{Colors.NC}")
        for tool_name, command in self.system_tools.items():
            if self.check_command(command):
                self.installed_system_tools.append(tool_name)
                print(f"{Colors.GREEN}✅ {tool_name} - INSTALLED{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}⚪ {tool_name} - not installed{Colors.NC}")
        
        # Check project files
        print(f"\n{Colors.CYAN}📁 Project Files:{Colors.NC}")
        project_files_to_check = [
            'ipsnipe.py',
            'ipsnipe/',
            'requirements.txt',
            'install.sh',
            'config.toml',
            'README.md',
            'LICENSE'
        ]
        
        for file_path in project_files_to_check:
            if os.path.exists(file_path):
                self.project_files.append(file_path)
                print(f"{Colors.GREEN}✅ {file_path} - FOUND{Colors.NC}")
        
        # Check for installed binaries in system paths
        system_binaries = ['/usr/local/bin/theHarvester', '/usr/local/bin/whatweb']
        for binary in system_binaries:
            if os.path.exists(binary):
                self.project_files.append(binary)
                print(f"{Colors.GREEN}✅ {binary} - FOUND{Colors.NC}")
    
    def confirm_uninstall(self):
        """Confirm what will be uninstalled"""
        print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
        print(f"{Colors.YELLOW}📋 Uninstall Summary{Colors.NC}\n")
        
        if not self.installed_python_packages and not self.installed_system_tools and not self.project_files:
            print(f"{Colors.GREEN}✨ No ipsnipe dependencies found to uninstall!{Colors.NC}")
            return False
        
        if self.installed_python_packages:
            print(f"{Colors.RED}🐍 Python packages to be REMOVED:{Colors.NC}")
            for package in self.installed_python_packages:
                print(f"   • {package}")
        
        if self.installed_system_tools:
            print(f"\n{Colors.RED}🛠️  System tools to be REMOVED:{Colors.NC}")
            for tool in self.installed_system_tools:
                print(f"   • {tool}")
        
        if self.project_files:
            print(f"\n{Colors.RED}📁 Project files to be REMOVED:{Colors.NC}")
            for file_path in self.project_files:
                print(f"   • {file_path}")
        
        print(f"\n{Colors.YELLOW}⚠️  WARNING: This will remove the above dependencies and files.{Colors.NC}")
        print(f"{Colors.YELLOW}Some tools might be used by other applications!{Colors.NC}")
        
        return True
    
    def ask_selective_removal(self):
        """Ask user if they want to keep any dependencies"""
        print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
        print(f"{Colors.BLUE}🤔 Do you want to keep any of these dependencies?{Colors.NC}")
        
        if self.installed_python_packages:
            response = input(f"{Colors.YELLOW}Keep Python packages? (y/N): {Colors.NC}").strip().lower()
            if response == 'y' or response == 'yes':
                print(f"\n{Colors.BLUE}Select Python packages to KEEP (press Enter when done):{Colors.NC}")
                for i, package in enumerate(self.installed_python_packages, 1):
                    print(f"   {i}. {package}")
                
                while True:
                    choice = input(f"{Colors.YELLOW}Enter package number to keep (or 'done'): {Colors.NC}").strip()
                    if choice.lower() == 'done' or choice == '':
                        break
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(self.installed_python_packages):
                            package = self.installed_python_packages[idx]
                            if package not in self.keep_packages:
                                self.keep_packages.append(package)
                                print(f"{Colors.GREEN}✅ Will keep: {package}{Colors.NC}")
                            else:
                                print(f"{Colors.YELLOW}⚠️  Already marked to keep: {package}{Colors.NC}")
                        else:
                            print(f"{Colors.RED}❌ Invalid choice{Colors.NC}")
                    except ValueError:
                        print(f"{Colors.RED}❌ Please enter a valid number or 'done'{Colors.NC}")
        
        if self.installed_system_tools:
            response = input(f"\n{Colors.YELLOW}Keep system tools? (y/N): {Colors.NC}").strip().lower()
            if response == 'y' or response == 'yes':
                print(f"\n{Colors.BLUE}Select system tools to KEEP (press Enter when done):{Colors.NC}")
                for i, tool in enumerate(self.installed_system_tools, 1):
                    print(f"   {i}. {tool}")
                
                while True:
                    choice = input(f"{Colors.YELLOW}Enter tool number to keep (or 'done'): {Colors.NC}").strip()
                    if choice.lower() == 'done' or choice == '':
                        break
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(self.installed_system_tools):
                            tool = self.installed_system_tools[idx]
                            if tool not in self.keep_tools:
                                self.keep_tools.append(tool)
                                print(f"{Colors.GREEN}✅ Will keep: {tool}{Colors.NC}")
                            else:
                                print(f"{Colors.YELLOW}⚠️  Already marked to keep: {tool}{Colors.NC}")
                        else:
                            print(f"{Colors.RED}❌ Invalid choice{Colors.NC}")
                    except ValueError:
                        print(f"{Colors.RED}❌ Please enter a valid number or 'done'{Colors.NC}")
    
    def final_confirmation(self):
        """Final confirmation before uninstall"""
        packages_to_remove = [p for p in self.installed_python_packages if p not in self.keep_packages]
        tools_to_remove = [t for t in self.installed_system_tools if t not in self.keep_tools]
        
        print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
        print(f"{Colors.YELLOW}📋 Final Uninstall Plan{Colors.NC}\n")
        
        if packages_to_remove:
            print(f"{Colors.RED}🐍 Python packages to REMOVE:{Colors.NC}")
            for package in packages_to_remove:
                print(f"   • {package}")
        
        if tools_to_remove:
            print(f"\n{Colors.RED}🛠️  System tools to REMOVE:{Colors.NC}")
            for tool in tools_to_remove:
                print(f"   • {tool}")
        
        if self.project_files:
            print(f"\n{Colors.RED}📁 Project files to REMOVE:{Colors.NC}")
            for file_path in self.project_files:
                print(f"   • {file_path}")
        
        if self.keep_packages:
            print(f"\n{Colors.GREEN}🐍 Python packages to KEEP:{Colors.NC}")
            for package in self.keep_packages:
                print(f"   • {package}")
        
        if self.keep_tools:
            print(f"\n{Colors.GREEN}🛠️  System tools to KEEP:{Colors.NC}")
            for tool in self.keep_tools:
                print(f"   • {tool}")
        
        if not packages_to_remove and not tools_to_remove and not self.project_files:
            print(f"{Colors.GREEN}✨ Nothing to uninstall!{Colors.NC}")
            return False
        
        print(f"\n{Colors.RED}⚠️  WARNING: This action cannot be undone!{Colors.NC}")
        response = input(f"{Colors.YELLOW}Proceed with uninstall? (y/N): {Colors.NC}").strip().lower()
        return response == 'y' or response == 'yes'
    
    def uninstall_python_packages(self):
        """Uninstall Python packages"""
        packages_to_remove = [p for p in self.installed_python_packages if p not in self.keep_packages]
        
        if not packages_to_remove:
            return
        
        print(f"\n{Colors.YELLOW}🐍 Uninstalling Python packages...{Colors.NC}")
        for package in packages_to_remove:
            try:
                print(f"   Removing {package}...")
                result = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', package], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ {package} removed successfully{Colors.NC}")
                else:
                    print(f"{Colors.YELLOW}⚠️  {package} - may not have been installed via pip{Colors.NC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to remove {package}: {e}{Colors.NC}")
    
    def uninstall_system_tools(self):
        """Uninstall system tools"""
        tools_to_remove = [t for t in self.installed_system_tools if t not in self.keep_tools]
        
        if not tools_to_remove:
            return
        
        print(f"\n{Colors.YELLOW}🛠️  Uninstalling system tools...{Colors.NC}")
        
        if self.os_type == 'debian':
            self.uninstall_debian_tools(tools_to_remove)
        elif self.os_type == 'macos':
            self.uninstall_macos_tools(tools_to_remove)
        elif self.os_type == 'arch':
            self.uninstall_arch_tools(tools_to_remove)
        else:
            print(f"{Colors.YELLOW}⚠️  Manual removal required for this OS{Colors.NC}")
            self.manual_tool_removal(tools_to_remove)
    
    def uninstall_debian_tools(self, tools):
        """Uninstall tools on Debian/Ubuntu"""
                    apt_tools = [tool for tool in tools if tool in ['nmap', 'ruby', 'whatweb']]
        
        if apt_tools:
            try:
                print(f"   Removing via apt: {', '.join(apt_tools)}")
                result = subprocess.run(['sudo', 'apt', 'remove', '-y'] + apt_tools, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ APT packages removed{Colors.NC}")
                else:
                    print(f"{Colors.RED}❌ Failed to remove some APT packages{Colors.NC}")
            except Exception as e:
                print(f"{Colors.RED}❌ APT removal failed: {e}{Colors.NC}")
        
        self.remove_manual_tools(tools)
    
    def uninstall_macos_tools(self, tools):
        """Uninstall tools on macOS"""
                    brew_tools = [tool for tool in tools if tool in ['nmap', 'feroxbuster', 'ffuf', 'ruby']]
        
        if brew_tools and shutil.which('brew'):
            try:
                print(f"   Removing via brew: {', '.join(brew_tools)}")
                result = subprocess.run(['brew', 'uninstall'] + brew_tools, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ Homebrew packages removed{Colors.NC}")
                else:
                    print(f"{Colors.RED}❌ Failed to remove some Homebrew packages{Colors.NC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Homebrew removal failed: {e}{Colors.NC}")
        
        self.remove_manual_tools(tools)
    
    def uninstall_arch_tools(self, tools):
        """Uninstall tools on Arch Linux"""
                    pacman_tools = [tool for tool in tools if tool in ['nmap', 'ruby', 'feroxbuster', 'ffuf', 'whatweb']]
        
        if pacman_tools:
            try:
                print(f"   Removing via pacman: {', '.join(pacman_tools)}")
                result = subprocess.run(['sudo', 'pacman', '-R', '--noconfirm'] + pacman_tools, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ Pacman packages removed{Colors.NC}")
                else:
                    print(f"{Colors.RED}❌ Failed to remove some pacman packages{Colors.NC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Pacman removal failed: {e}{Colors.NC}")
        
        self.remove_manual_tools(tools)
    
    def remove_manual_tools(self, tools):
        """Remove manually installed tools"""
        manual_tools = ['theHarvester', 'whatweb']
        manual_binaries = {
            'theHarvester': '/usr/local/bin/theHarvester',
            'whatweb': '/usr/local/bin/whatweb'
        }
        
        for tool in tools:
            if tool in manual_tools and tool in manual_binaries:
                binary_path = manual_binaries[tool]
                if os.path.exists(binary_path):
                    try:
                        os.remove(binary_path)
                        print(f"{Colors.GREEN}✅ Removed {binary_path}{Colors.NC}")
                    except Exception as e:
                        print(f"{Colors.RED}❌ Failed to remove {binary_path}: {e}{Colors.NC}")
    
    def manual_tool_removal(self, tools):
        """Provide manual removal instructions"""
        print(f"\n{Colors.BLUE}📋 Manual removal required for:{Colors.NC}")
        for tool in tools:
            print(f"   • {tool} - Please remove manually using your system's package manager")
    
    def remove_project_files(self):
        """Remove project files"""
        if not self.project_files:
            return
        
        print(f"\n{Colors.YELLOW}📁 Removing project files...{Colors.NC}")
        for file_path in self.project_files:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"{Colors.GREEN}✅ Removed file: {file_path}{Colors.NC}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"{Colors.GREEN}✅ Removed directory: {file_path}{Colors.NC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to remove {file_path}: {e}{Colors.NC}")
    
    def run(self):
        """Run the uninstaller"""
        self.print_banner()
        
        print(f"{Colors.BLUE}This script will help you safely remove ipsnipe and its dependencies.{Colors.NC}")
        print(f"{Colors.YELLOW}⚠️  Note: Some tools may be used by other applications!{Colors.NC}\n")
        
        # Scan for dependencies
        self.scan_installed_dependencies()
        
        # Confirm what will be uninstalled
        if not self.confirm_uninstall():
            print(f"\n{Colors.GREEN}✨ Uninstall complete - nothing to remove!{Colors.NC}")
            return
        
        # Ask about selective removal
        self.ask_selective_removal()
        
        # Final confirmation
        if not self.final_confirmation():
            print(f"\n{Colors.BLUE}💡 Uninstall cancelled.{Colors.NC}")
            return
        
        # Perform uninstall
        print(f"\n{Colors.GREEN}🚀 Starting uninstall process...{Colors.NC}")
        
        self.uninstall_python_packages()
        self.uninstall_system_tools()
        self.remove_project_files()
        
        print(f"\n{Colors.GREEN}✅ Uninstall completed successfully!{Colors.NC}")
        print(f"{Colors.BLUE}Thank you for using ipsnipe! 🚀{Colors.NC}")


def main():
    """Main entry point"""
    try:
        uninstaller = IPSnipeUninstaller()
        uninstaller.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Uninstall cancelled by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Uninstall failed: {e}{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main() 