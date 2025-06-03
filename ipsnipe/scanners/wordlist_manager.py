#!/usr/bin/env python3
"""
Wordlist manager for ipsnipe
Handles cewl integration, wordlist selection, and custom wordlist options
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ..ui.colors import Colors


class WordlistManager:
    """Manages wordlist generation and selection including cewl integration"""
    
    def __init__(self, config: Dict, output_dir: str):
        self.config = config
        self.output_dir = output_dir
        self.generated_cewl_wordlist = None
        self.discovered_domains = []
        self.web_ports = []
    
    def set_discovered_domains(self, domains: List[str]):
        """Set discovered domains for cewl generation"""
        self.discovered_domains = domains
    
    def set_web_ports(self, ports: List[int]):
        """Set web ports for cewl generation"""
        self.web_ports = ports
    
    def check_cewl_available(self) -> bool:
        """Check if cewl is available on the system"""
        try:
            result = subprocess.run(['which', 'cewl'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def generate_cewl_wordlist(self, target_url: str, depth: int = 2, min_word_length: int = 5, 
                              max_word_length: int = 15, output_filename: str = None) -> Optional[str]:
        """Generate a custom wordlist using cewl from target website"""
        
        if not self.check_cewl_available():
            print(f"{Colors.RED}❌ cewl not found - please install it first{Colors.END}")
            print(f"{Colors.CYAN}💡 Install with: sudo apt install cewl{Colors.END}")
            return None
        
        # Determine output filename
        if not output_filename:
            domain_name = target_url.replace('http://', '').replace('https://', '').replace(':', '_').replace('/', '_')
            output_filename = f"cewl_wordlist_{domain_name}.txt"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print(f"{Colors.CYAN}🕷️  Generating custom wordlist with cewl...{Colors.END}")
        print(f"{Colors.YELLOW}📊 Target: {target_url}{Colors.END}")
        print(f"{Colors.YELLOW}📊 Depth: {depth} levels{Colors.END}")
        print(f"{Colors.YELLOW}📊 Word length: {min_word_length}-{max_word_length} characters{Colors.END}")
        print(f"{Colors.YELLOW}📄 Output: {output_filename}{Colors.END}")
        
        # Build cewl command
        command = [
            'cewl',
            '--depth', str(depth),
            '--min_word_length', str(min_word_length),
            '--max_word_length', str(max_word_length),
            '--write', output_path,
            '--lowercase',  # Convert to lowercase
            '--with-numbers',  # Include words with numbers
            target_url
        ]
        
        try:
            print(f"{Colors.CYAN}⏳ Running cewl (this may take a minute)...{Colors.END}")
            
            # Run cewl with timeout
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minute timeout
                cwd=self.output_dir
            )
            
            if result.returncode == 0:
                # Check if wordlist was generated and has content
                if os.path.exists(output_path):
                    word_count = self._count_words_in_file(output_path)
                    if word_count > 0:
                        print(f"{Colors.GREEN}✅ Custom wordlist generated successfully{Colors.END}")
                        print(f"{Colors.GREEN}📊 Generated {word_count} unique words{Colors.END}")
                        print(f"{Colors.CYAN}📄 Saved to: {output_path}{Colors.END}")
                        self.generated_cewl_wordlist = output_path
                        return output_path
                    else:
                        print(f"{Colors.YELLOW}⚠️  Wordlist generated but appears empty{Colors.END}")
                        return None
                else:
                    print(f"{Colors.RED}❌ Wordlist file not created{Colors.END}")
                    return None
            else:
                print(f"{Colors.RED}❌ cewl failed with error:{Colors.END}")
                print(f"{Colors.RED}{result.stderr}{Colors.END}")
                return None
        
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}⏰ cewl timed out - target may be slow or unresponsive{Colors.END}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error running cewl: {str(e)}{Colors.END}")
            return None
    
    def _count_words_in_file(self, file_path: str) -> int:
        """Count number of words in a wordlist file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len([line.strip() for line in f if line.strip()])
        except Exception:
            return 0
    
    def get_wordlist_options(self) -> Dict[str, str]:
        """Get available wordlist options including cewl-generated ones"""
        options = {}
        
        # Default wordlists from config
        wordlist_config = self.config.get('wordlists', {})
        
        # Add standard options
        for key, path in wordlist_config.items():
            if key != 'base_dir' and os.path.exists(path):
                word_count = self._count_words_in_file(path)
                options[key] = f"{path} ({word_count} words)"
        
        # Add cewl-generated wordlist if available
        if self.generated_cewl_wordlist and os.path.exists(self.generated_cewl_wordlist):
            word_count = self._count_words_in_file(self.generated_cewl_wordlist)
            options['cewl_generated'] = f"{self.generated_cewl_wordlist} ({word_count} words)"
        
        return options
    
    def prompt_wordlist_selection(self, tool_name: str = "directory enumeration") -> Tuple[str, str]:
        """
        Prompt user to select wordlist type after domain discovery
        Returns tuple of (wordlist_type, wordlist_path)
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}📚 Wordlist Selection for {tool_name.title()}{Colors.END}")
        print(f"{Colors.CYAN}═══════════════════════════════════════════════════════{Colors.END}")
        
        # Check if we can generate cewl wordlist
        can_generate_cewl = (
            self.check_cewl_available() and 
            (self.discovered_domains or self.web_ports)
        )
        
        if can_generate_cewl and not self.generated_cewl_wordlist:
            print(f"{Colors.GREEN}🕷️  cewl is available and web content detected!{Colors.END}")
            print(f"{Colors.CYAN}💡 cewl can generate a custom wordlist from the target website{Colors.END}")
            
            # Offer to generate cewl wordlist
            while True:
                choice = input(f"\n{Colors.YELLOW}Generate custom wordlist with cewl? (y/N): {Colors.END}").strip().lower()
                
                if choice in ['y', 'yes']:
                    # Determine best target URL for cewl
                    target_url = self._get_best_cewl_target()
                    if target_url:
                        cewl_path = self.generate_cewl_wordlist(target_url)
                        if cewl_path:
                            print(f"{Colors.GREEN}✨ Using cewl-generated wordlist for {tool_name}{Colors.END}")
                            return 'cewl_generated', cewl_path
                        else:
                            print(f"{Colors.YELLOW}⚠️  cewl generation failed, falling back to standard wordlists{Colors.END}")
                    break
                elif choice in ['n', 'no', '']:
                    break
                else:
                    print(f"{Colors.RED}Please enter 'y' or 'n'{Colors.END}")
        
        # Show available wordlist options
        options = self.get_wordlist_options()
        
        if not options:
            print(f"{Colors.YELLOW}⚠️  No wordlists found, will create minimal fallback{Colors.END}")
            return 'minimal', self._create_minimal_wordlist()
        
        print(f"\n{Colors.BOLD}Available wordlist options:{Colors.END}")
        
        # Create numbered menu
        option_keys = list(options.keys())
        for i, (key, description) in enumerate(options.items(), 1):
            size_indicator = ""
            if 'common' in key or 'small' in key:
                size_indicator = f" {Colors.GREEN}(fast){Colors.END}"
            elif 'medium' in key:
                size_indicator = f" {Colors.YELLOW}(medium){Colors.END}"
            elif 'big' in key or 'large' in key:
                size_indicator = f" {Colors.RED}(slow){Colors.END}"
            elif 'cewl' in key:
                size_indicator = f" {Colors.PURPLE}(custom){Colors.END}"
            
            print(f"  {Colors.CYAN}{i}) {key.replace('_', ' ').title()}{Colors.END}{size_indicator}")
            print(f"     {Colors.CYAN}{description}{Colors.END}")
        
        # Add custom wordlist option
        custom_option = len(options) + 1
        print(f"  {Colors.CYAN}{custom_option}) Custom wordlist{Colors.END} {Colors.YELLOW}(specify path){Colors.END}")
        
        # Get user selection
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}Select wordlist (1-{custom_option}, default: 1): {Colors.END}").strip()
                
                if not choice:
                    choice = "1"
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(options):
                    selected_key = option_keys[choice_num - 1]
                    wordlist_path = self._get_wordlist_path_by_key(selected_key)
                    
                    if wordlist_path and os.path.exists(wordlist_path):
                        word_count = self._count_words_in_file(wordlist_path)
                        print(f"{Colors.GREEN}✅ Selected: {selected_key.replace('_', ' ').title()} ({word_count} words){Colors.END}")
                        return selected_key, wordlist_path
                    else:
                        print(f"{Colors.RED}❌ Wordlist file not found: {wordlist_path}{Colors.END}")
                        continue
                
                elif choice_num == custom_option:
                    # Custom wordlist path
                    custom_path = input(f"{Colors.CYAN}Enter custom wordlist path: {Colors.END}").strip()
                    
                    if custom_path and os.path.exists(custom_path):
                        word_count = self._count_words_in_file(custom_path)
                        print(f"{Colors.GREEN}✅ Using custom wordlist ({word_count} words){Colors.END}")
                        return 'custom', custom_path
                    else:
                        print(f"{Colors.RED}❌ Custom wordlist file not found: {custom_path}{Colors.END}")
                        continue
                
                else:
                    print(f"{Colors.RED}❌ Invalid selection. Please choose 1-{custom_option}{Colors.END}")
            
            except ValueError:
                print(f"{Colors.RED}❌ Please enter a valid number{Colors.END}")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⏭️  Using default wordlist{Colors.END}")
                return self._get_default_wordlist()
    
    def _get_best_cewl_target(self) -> Optional[str]:
        """Determine the best target URL for cewl generation"""
        if self.discovered_domains:
            # Use the first discovered domain with preferred protocol
            domain = self.discovered_domains[0]
            
            # Try HTTPS first, then HTTP
            for protocol in ['https', 'http']:
                for port in [443, 80] + self.web_ports:
                    if (protocol == 'https' and port in [443, 8443]) or (protocol == 'http' and port in [80, 8080]):
                        url = f"{protocol}://{domain}"
                        if port not in [80, 443]:
                            url += f":{port}"
                        return url
            
            # Fallback to basic HTTP
            return f"http://{domain}"
        
        return None
    
    def _get_wordlist_path_by_key(self, key: str) -> Optional[str]:
        """Get wordlist path by key"""
        if key == 'cewl_generated':
            return self.generated_cewl_wordlist
        
        wordlist_config = self.config.get('wordlists', {})
        return wordlist_config.get(key)
    
    def _get_default_wordlist(self) -> Tuple[str, str]:
        """Get default wordlist fallback"""
        wordlist_config = self.config.get('wordlists', {})
        
        # Try common first, then small, then any available
        for key in ['common', 'small', 'ferox_small']:
            if key in wordlist_config:
                path = wordlist_config[key]
                if os.path.exists(path):
                    return key, path
        
        # Last resort - create minimal wordlist
        return 'minimal', self._create_minimal_wordlist()
    
    def _create_minimal_wordlist(self) -> str:
        """Create a minimal wordlist as fallback"""
        minimal_words = [
            'admin', 'login', 'index', 'home', 'test', 'backup', 'config', 'data',
            'api', 'upload', 'download', 'files', 'images', 'js', 'css', 'assets',
            'static', 'robots.txt', 'sitemap.xml', 'favicon.ico', '.htaccess',
            'phpmyadmin', 'wp-admin', 'administrator', 'panel', 'dashboard'
        ]
        
        minimal_path = os.path.join(self.output_dir, 'minimal_wordlist.txt')
        
        try:
            with open(minimal_path, 'w') as f:
                f.write('\n'.join(minimal_words))
            
            print(f"{Colors.YELLOW}⚠️  Created minimal wordlist: {minimal_path}{Colors.END}")
            return minimal_path
        
        except Exception as e:
            print(f"{Colors.RED}❌ Error creating minimal wordlist: {str(e)}{Colors.END}")
            return None
    
    def cleanup_generated_wordlists(self):
        """Clean up generated wordlists at the end of scanning"""
        if self.generated_cewl_wordlist and os.path.exists(self.generated_cewl_wordlist):
            print(f"{Colors.CYAN}🧹 Keeping cewl-generated wordlist: {self.generated_cewl_wordlist}{Colors.END}")
            print(f"{Colors.CYAN}💡 You can reuse this wordlist for future scans of the same target{Colors.END}") 