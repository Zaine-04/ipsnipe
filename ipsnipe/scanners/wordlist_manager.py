#!/usr/bin/env python3
"""
Wordlist manager for ipsnipe - HTB-Optimized Edition
Handles intelligent wordlist detection, cewl integration, and HTB-specific paths
"""

import subprocess
import os
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ..ui.colors import Colors


class WordlistManager:
    """Manages wordlist generation and selection with HTB-optimized auto-detection"""
    
    def __init__(self, config: Dict, output_dir: str):
        self.config = config
        self.output_dir = output_dir
        self.generated_cewl_wordlist = None
        self.discovered_domains = []
        self.web_ports = []
        self.detected_wordlists = None
        self._detect_wordlist_locations()
    
    def _detect_wordlist_locations(self):
        """Auto-detect SecLists and other wordlist collections in HTB environments"""
        print(f"{Colors.CYAN}🔍 Auto-detecting wordlist locations...{Colors.END}")
        
        detected = {
            'seclists_base': None,
            'dirb_base': None,
            'dirbuster_base': None,
            'custom_base': None,
            'available_lists': {}
        }
        
        # Common HTB/Kali wordlist locations to check
        search_paths = [
            '/usr/share/seclists',
            '/usr/share/wordlists/seclists', 
            '/usr/share/wordlists',
            '/opt/SecLists',
            '/opt/seclists',
            '/home/kali/wordlists',
            '/root/wordlists',
            '~/wordlists',
            './wordlists'
        ]
        
        # Expand home directory paths
        expanded_paths = []
        for path in search_paths:
            if path.startswith('~/'):
                expanded_paths.append(os.path.expanduser(path))
            else:
                expanded_paths.append(path)
        
        # Detect SecLists (most important for HTB)
        for base_path in expanded_paths:
            seclists_web_content = os.path.join(base_path, 'Discovery', 'Web-Content')
            if os.path.exists(seclists_web_content):
                detected['seclists_base'] = base_path
                print(f"{Colors.GREEN}✅ SecLists detected: {base_path}{Colors.END}")
                
                # Use enhanced analysis for SecLists
                print(f"{Colors.CYAN}🔬 Performing deep analysis of SecLists structure...{Colors.END}")
                enhanced_analysis = self._analyze_wordlist_directory_structure(base_path)
                detected['available_lists'].update(enhanced_analysis)
                break
        
        # Detect dirb wordlists
        for base_path in expanded_paths:
            dirb_path = os.path.join(base_path, 'dirb')
            if os.path.exists(dirb_path):
                detected['dirb_base'] = dirb_path
                print(f"{Colors.GREEN}✅ Dirb wordlists detected: {dirb_path}{Colors.END}")
                
                # Enhanced analysis for dirb
                dirb_analysis = self._analyze_wordlist_directory_structure(dirb_path)
                detected['available_lists'].update(dirb_analysis)
                break
        
        # Detect dirbuster wordlists  
        for base_path in expanded_paths:
            dirbuster_path = os.path.join(base_path, 'dirbuster')
            if os.path.exists(dirbuster_path):
                detected['dirbuster_base'] = dirbuster_path
                print(f"{Colors.GREEN}✅ DirBuster wordlists detected: {dirbuster_path}{Colors.END}")
                
                # Enhanced analysis for dirbuster
                dirbuster_analysis = self._analyze_wordlist_directory_structure(dirbuster_path)
                detected['available_lists'].update(dirbuster_analysis)
                break
        
        # Legacy categorization for SecLists (maintain compatibility)
        if detected['seclists_base'] and not detected['available_lists']:
            detected['available_lists'] = self._categorize_seclists_wordlists(detected['seclists_base'])
        
        # Add classic wordlists as fallbacks if enhanced analysis didn't find them
        if not any('dirb' in key for key in detected['available_lists'].keys()):
            self._add_classic_wordlists(detected)
        
        # Check for any general wordlist directories and analyze them
        for base_path in expanded_paths:
            if os.path.exists(base_path) and base_path not in [detected['seclists_base'], detected['dirb_base'], detected['dirbuster_base']]:
                if any(os.path.isfile(os.path.join(base_path, f)) for f in os.listdir(base_path) if f.endswith('.txt')):
                    print(f"{Colors.CYAN}🔍 Analyzing additional wordlist directory: {base_path}{Colors.END}")
                    additional_analysis = self._analyze_wordlist_directory_structure(base_path)
                    detected['available_lists'].update(additional_analysis)
        
        # Sort by quality score for better recommendations
        if detected['available_lists']:
            sorted_lists = dict(sorted(
                detected['available_lists'].items(), 
                key=lambda x: x[1].get('quality_score', 0), 
                reverse=True
            ))
            detected['available_lists'] = sorted_lists
        
        self.detected_wordlists = detected
        
        # Enhanced summary of detection
        total_found = len(detected['available_lists'])
        if total_found > 0:
            print(f"{Colors.GREEN}🎯 Enhanced wordlist detection complete: {total_found} intelligent wordlists categorized{Colors.END}")
            
            # Show breakdown by category
            categories = {}
            for wordlist_info in detected['available_lists'].values():
                purpose = wordlist_info.get('purpose', 'unknown')
                categories[purpose] = categories.get(purpose, 0) + 1
            
            category_summary = ", ".join([f"{count} {purpose}" for purpose, count in categories.items()])
            print(f"{Colors.CYAN}📊 Categories found: {category_summary}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  No standard wordlist locations found - will create minimal fallbacks{Colors.END}")
    
    def _categorize_seclists_wordlists(self, seclists_base: str) -> Dict[str, Dict]:
        """Intelligently categorize SecLists wordlists by purpose and size"""
        web_content_path = os.path.join(seclists_base, 'Discovery', 'Web-Content')
        dns_path = os.path.join(seclists_base, 'Discovery', 'DNS')
        
        categories = {
            # HTB Champion Lists (proven in HTB community)
            'htb_champion': {
                'path': os.path.join(web_content_path, 'directory-list-2.3-medium.txt'),
                'description': 'HTB Community Favorite - Medium coverage, fast results',
                'size': 'medium',
                'purpose': 'directory',
                'speed': 'fast'
            },
            
            # Speed-optimized for initial recon
            'htb_speed': {
                'path': os.path.join(web_content_path, 'common.txt'),
                'description': 'Lightning Fast - Common directories (30 seconds)',
                'size': 'small',
                'purpose': 'directory', 
                'speed': 'lightning'
            },
            
            # Balanced approach
            'htb_balanced': {
                'path': os.path.join(web_content_path, 'raft-medium-directories.txt'),
                'description': 'Balanced Coverage - Different ordering than DirList',
                'size': 'medium',
                'purpose': 'directory',
                'speed': 'balanced'
            },
            
            # Comprehensive when stuck
            'htb_comprehensive': {
                'path': os.path.join(web_content_path, 'directory-list-2.3-big.txt'),
                'description': 'Maximum Coverage - When nothing else works',
                'size': 'large',
                'purpose': 'directory',
                'speed': 'slow'
            },
            
            # File-focused enumeration
            'htb_files': {
                'path': os.path.join(web_content_path, 'raft-medium-files.txt'),
                'description': 'File Discovery - Config files, backups, etc.',
                'size': 'medium',
                'purpose': 'files',
                'speed': 'balanced'
            },
            
            # API discovery
            'htb_api': {
                'path': os.path.join(web_content_path, 'api', 'api-endpoints.txt'),
                'description': 'API Endpoints - Modern web apps',
                'size': 'small',
                'purpose': 'api',
                'speed': 'fast'
            },
            
            # Subdomain enumeration
            'htb_subdomains': {
                'path': os.path.join(dns_path, 'bitquark-subdomains-top100000.txt'),
                'description': 'Subdomain Discovery - Virtual hosts',
                'size': 'large',
                'purpose': 'subdomain',
                'speed': 'slow'
            },
            
            # Quick subdomain check
            'htb_subdomains_quick': {
                'path': os.path.join(dns_path, 'subdomains-top1million-5000.txt'),
                'description': 'Quick Subdomain Check - Top 5000',
                'size': 'small',
                'purpose': 'subdomain',
                'speed': 'fast'
            }
        }
        
        # Filter to only include wordlists that actually exist
        available = {}
        for name, info in categories.items():
            if os.path.exists(info['path']):
                word_count = self._count_words_in_file(info['path'])
                info['word_count'] = word_count
                info['file_size'] = os.path.getsize(info['path'])
                available[name] = info
                
        return available
    
    def _add_classic_wordlists(self, detected: Dict):
        """Add classic dirb/dirbuster wordlists as fallbacks"""
        classic_lists = {}
        
        # Dirb wordlists
        if detected['dirb_base']:
            dirb_lists = {
                'dirb_common': {
                    'path': os.path.join(detected['dirb_base'], 'common.txt'),
                    'description': 'Dirb Classic - Time-tested common paths',
                    'size': 'small',
                    'purpose': 'directory',
                    'speed': 'fast'
                },
                'dirb_big': {
                    'path': os.path.join(detected['dirb_base'], 'big.txt'),
                    'description': 'Dirb Extended - Larger coverage',
                    'size': 'medium', 
                    'purpose': 'directory',
                    'speed': 'balanced'
                }
            }
            
            for name, info in dirb_lists.items():
                if os.path.exists(info['path']):
                    word_count = self._count_words_in_file(info['path'])
                    info['word_count'] = word_count
                    info['file_size'] = os.path.getsize(info['path'])
                    classic_lists[name] = info
        
        # DirBuster wordlists
        if detected['dirbuster_base']:
            dirbuster_lists = {
                'dirbuster_medium': {
                    'path': os.path.join(detected['dirbuster_base'], 'directory-list-2.3-medium.txt'),
                    'description': 'DirBuster Medium - Classic directory list',
                    'size': 'medium',
                    'purpose': 'directory',
                    'speed': 'balanced'
                }
            }
            
            for name, info in dirbuster_lists.items():
                if os.path.exists(info['path']):
                    word_count = self._count_words_in_file(info['path'])
                    info['word_count'] = word_count
                    info['file_size'] = os.path.getsize(info['path'])
                    classic_lists[name] = info
        
        # Add classic lists to available lists
        if 'available_lists' not in detected:
            detected['available_lists'] = {}
        detected['available_lists'].update(classic_lists)
    
    def get_recommended_wordlist(self, scan_type: str = 'directory', priority: str = 'balanced') -> Tuple[str, str]:
        """Get intelligently recommended wordlist based on scan type, priority, and quality analysis"""
        if not self.detected_wordlists or not self.detected_wordlists['available_lists']:
            return self._get_default_wordlist()
        
        available = self.detected_wordlists['available_lists']
        
        # Filter wordlists by purpose
        purpose_matches = {
            name: info for name, info in available.items()
            if info.get('purpose', 'directory') == scan_type
        }
        
        # If no exact purpose matches, use directory wordlists as fallback
        if not purpose_matches and scan_type != 'directory':
            purpose_matches = {
                name: info for name, info in available.items()
                if info.get('purpose', 'directory') == 'directory'
            }
        
        # If still no matches, use any available wordlist
        if not purpose_matches:
            purpose_matches = available
        
        # Enhanced recommendations based on priority and quality scores
        priority_filters = {
            'speed': lambda info: info.get('speed') in ['lightning', 'fast'] and info.get('word_count', 0) <= 5000,
            'balanced': lambda info: info.get('speed') in ['fast', 'balanced'] and 1000 <= info.get('word_count', 0) <= 50000,
            'comprehensive': lambda info: info.get('word_count', 0) >= 10000
        }
        
        # Apply priority filter
        priority_filter = priority_filters.get(priority, priority_filters['balanced'])
        filtered_matches = {
            name: info for name, info in purpose_matches.items()
            if priority_filter(info)
        }
        
        # If no matches after filtering, use original purpose matches
        if not filtered_matches:
            filtered_matches = purpose_matches
        
        # Sort by quality score and select the best
        if filtered_matches:
            best_match = max(
                filtered_matches.items(),
                key=lambda x: (
                    x[1].get('quality_score', 0),  # Primary: quality score
                    -x[1].get('word_count', float('inf')) if priority == 'speed' else x[1].get('word_count', 0)  # Secondary: word count based on priority
                )
            )
            
            name, info = best_match
            return name, info['path']
        
        # Legacy fallback for compatibility
        legacy_recommendations = {
            'directory': {
                'speed': ['htb_speed', 'dirb_common', 'htb_champion'],
                'balanced': ['htb_champion', 'htb_balanced', 'dirbuster_medium'],
                'comprehensive': ['htb_comprehensive', 'htb_champion', 'dirb_big']
            },
            'files': {
                'speed': ['htb_files', 'htb_speed', 'dirb_common'],
                'balanced': ['htb_files', 'htb_champion'],
                'comprehensive': ['htb_files', 'htb_comprehensive']
            },
            'api': {
                'speed': ['htb_api', 'htb_speed'],
                'balanced': ['htb_api', 'htb_champion'],
                'comprehensive': ['htb_api', 'htb_comprehensive']
            },
            'subdomain': {
                'speed': ['htb_subdomains_quick'],
                'balanced': ['htb_subdomains_quick', 'htb_subdomains'],
                'comprehensive': ['htb_subdomains']
            }
        }
        
        # Legacy recommendation logic
        rec_list = legacy_recommendations.get(scan_type, {}).get(priority, ['htb_champion', 'htb_speed', 'dirb_common'])
        
        for wordlist_name in rec_list:
            if wordlist_name in available:
                wordlist_info = available[wordlist_name]
                return wordlist_name, wordlist_info['path']
        
        # Final fallback to any available wordlist
        if available:
            first_available = list(available.keys())[0]
            return first_available, available[first_available]['path']
        
        # Ultimate fallback
        return self._get_default_wordlist()
    
    def set_discovered_domains(self, domains: List[str]):
        """Set discovered domains for cewl generation"""
        self.discovered_domains = domains
    
    def set_web_ports(self, ports: List[int]):
        """Set web ports for cewl generation"""
        self.web_ports = ports
    
    def check_cewl_available(self) -> bool:
        """Check if cewl is available on the system with improved detection"""
        try:
            # Try multiple methods to detect cewl
            detection_methods = [
                ['which', 'cewl'],
                ['whereis', 'cewl'],
                ['command', '-v', 'cewl']
            ]
            
            for method in detection_methods:
                try:
                    result = subprocess.run(method, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and result.stdout.strip():
                        print(f"{Colors.GREEN}✅ CeWL found: {result.stdout.strip().split()[0]}{Colors.END}")
                        return True
                except:
                    continue
            
            # Try direct execution as final check
            try:
                result = subprocess.run(['cewl', '--help'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0 or 'cewl' in result.stderr.lower():
                    print(f"{Colors.GREEN}✅ CeWL available (direct execution test){Colors.END}")
                    return True
            except:
                pass
                
            print(f"{Colors.YELLOW}⚠️  CeWL not found in PATH{Colors.END}")
            return False
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error checking for CeWL: {str(e)}{Colors.END}")
            return False
    
    def generate_cewl_wordlist(self, target_url: str, depth: int = 2, min_word_length: int = 5, 
                              max_word_length: int = 15, output_filename: str = None) -> Optional[str]:
        """Generate a custom wordlist using cewl from target website with robust error handling"""
        
        if not self.check_cewl_available():
            print(f"{Colors.RED}❌ CeWL not found - please install it first{Colors.END}")
            print(f"{Colors.CYAN}💡 Install with: sudo apt install cewl{Colors.END}")
            print(f"{Colors.CYAN}💡 Or: gem install cewl{Colors.END}")
            return None
        
        # Validate and clean target URL
        target_url = target_url.strip()
        if not target_url.startswith(('http://', 'https://')):
            # Try HTTPS first, then HTTP
            test_urls = [f"https://{target_url}", f"http://{target_url}"]
            working_url = None
            
            for test_url in test_urls:
                try:
                    print(f"{Colors.CYAN}🔍 Testing URL accessibility: {test_url}{Colors.END}")
                    import urllib.request
                    import urllib.error
                    
                    # Simple connectivity test
                    request = urllib.request.Request(test_url, headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; CeWL)'
                    })
                    
                    with urllib.request.urlopen(request, timeout=10) as response:
                        if response.status == 200:
                            working_url = test_url
                            print(f"{Colors.GREEN}✅ URL accessible: {test_url}{Colors.END}")
                            break
                        
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠️  URL test failed for {test_url}: {str(e)}{Colors.END}")
                    continue
            
            if working_url:
                target_url = working_url
            else:
                print(f"{Colors.RED}❌ Target URL not accessible. Using original URL anyway...{Colors.END}")
                target_url = test_urls[0]  # Default to HTTPS
        
        # Determine output filename with safer character replacement
        if not output_filename:
            # More robust domain extraction and cleaning
            import re
            domain_clean = re.sub(r'[^\w\-_.]', '_', target_url)
            domain_clean = re.sub(r'_+', '_', domain_clean)  # Replace multiple underscores
            domain_clean = domain_clean.strip('_')
            output_filename = f"cewl_wordlist_{domain_clean}.txt"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Remove existing file if it exists
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Could not remove existing file: {str(e)}{Colors.END}")
        
        print(f"{Colors.CYAN}🕷️  Generating custom wordlist with CeWL...{Colors.END}")
        print(f"{Colors.YELLOW}📊 Target: {target_url}{Colors.END}")
        print(f"{Colors.YELLOW}📊 Depth: {depth} levels{Colors.END}")
        print(f"{Colors.YELLOW}📊 Word length: {min_word_length}-{max_word_length} characters{Colors.END}")
        print(f"{Colors.YELLOW}📄 Output: {output_path}{Colors.END}")
        
        # Build cewl command with improved parameters
        command = [
            'cewl',
            '--depth', str(depth),
            '--min_word_length', str(min_word_length),
            '--max_word_length', str(max_word_length),
            '--write', output_path,
            '--lowercase',      # Convert to lowercase
            '--with-numbers',   # Include words with numbers
            '--verbose',        # Verbose output for debugging
            '--user-agent', 'Mozilla/5.0 (compatible; CeWL/ipsnipe)',  # Custom user agent
            target_url
        ]
        
        try:
            print(f"{Colors.CYAN}⏳ Running CeWL (this may take a minute)...{Colors.END}")
            print(f"{Colors.CYAN}🔧 Command: {' '.join(command)}{Colors.END}")
            
            # Run cewl with improved error handling
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=600,  # Increased timeout to 10 minutes
                cwd=self.output_dir,
                env=os.environ.copy()  # Inherit environment variables
            )
            
            # Debug output
            if result.stdout:
                print(f"{Colors.CYAN}📤 CeWL stdout: {result.stdout[:200]}...{Colors.END}")
            if result.stderr:
                print(f"{Colors.YELLOW}📤 CeWL stderr: {result.stderr[:200]}...{Colors.END}")
            
            # Check result more thoroughly
            if result.returncode == 0:
                # Check if wordlist was generated and has content
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    word_count = self._count_words_in_file(output_path)
                    
                    if word_count > 0:
                        print(f"{Colors.GREEN}✅ Custom wordlist generated successfully{Colors.END}")
                        print(f"{Colors.GREEN}📊 Generated {word_count} unique words{Colors.END}")
                        print(f"{Colors.GREEN}📏 File size: {file_size} bytes{Colors.END}")
                        print(f"{Colors.CYAN}📄 Saved to: {output_path}{Colors.END}")
                        self.generated_cewl_wordlist = output_path
                        return output_path
                    else:
                        print(f"{Colors.YELLOW}⚠️  Wordlist file created but appears empty (size: {file_size} bytes){Colors.END}")
                        # Check if file has any content at all
                        try:
                            with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().strip()
                                if content:
                                    print(f"{Colors.YELLOW}📄 File has content but no valid words found{Colors.END}")
                                    print(f"{Colors.YELLOW}📄 Sample content: {content[:100]}...{Colors.END}")
                        except Exception as e:
                            print(f"{Colors.RED}❌ Error reading generated file: {str(e)}{Colors.END}")
                        return None
                else:
                    print(f"{Colors.RED}❌ Wordlist file not created at expected location: {output_path}{Colors.END}")
                    # Check if file was created elsewhere
                    possible_files = []
                    for file in os.listdir(self.output_dir):
                        if file.startswith('cewl') and file.endswith('.txt'):
                            possible_files.append(file)
                    
                    if possible_files:
                        print(f"{Colors.YELLOW}📄 Found possible CeWL output files: {possible_files}{Colors.END}")
                    
                    return None
            else:
                print(f"{Colors.RED}❌ CeWL failed with return code: {result.returncode}{Colors.END}")
                print(f"{Colors.RED}📄 Error output: {result.stderr}{Colors.END}")
                print(f"{Colors.RED}📄 Standard output: {result.stdout}{Colors.END}")
                
                # Try to diagnose common issues
                if 'connection' in result.stderr.lower() or 'network' in result.stderr.lower():
                    print(f"{Colors.YELLOW}💡 Network connectivity issue - check target URL accessibility{Colors.END}")
                elif 'permission' in result.stderr.lower():
                    print(f"{Colors.YELLOW}💡 Permission issue - check write permissions for {self.output_dir}{Colors.END}")
                elif 'timeout' in result.stderr.lower():
                    print(f"{Colors.YELLOW}💡 Timeout issue - target may be slow, try reducing depth{Colors.END}")
                    
                return None
        
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}⏰ CeWL timed out after 10 minutes{Colors.END}")
            print(f"{Colors.YELLOW}💡 Target may be slow or unresponsive, try reducing depth or using a different target{Colors.END}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error running CeWL: {str(e)}{Colors.END}")
            print(f"{Colors.YELLOW}💡 Debug info: Command was {' '.join(command)}{Colors.END}")
            return None
    
    def _count_words_in_file(self, file_path: str) -> int:
        """Count number of words in a wordlist file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len([line.strip() for line in f if line.strip()])
        except Exception:
            return 0
    
    def get_wordlist_options(self) -> Dict[str, str]:
        """Get available wordlist options including cewl-generated and auto-detected ones"""
        options = {}
        
        # Add auto-detected intelligent wordlists (prioritized)
        if self.detected_wordlists and self.detected_wordlists['available_lists']:
            for name, info in self.detected_wordlists['available_lists'].items():
                if os.path.exists(info['path']):
                    size_emoji = {'small': '⚡', 'medium': '⚖️', 'large': '🔋'}
                    purpose_emoji = {'directory': '📁', 'files': '📄', 'api': '🔌', 'subdomain': '🌐'}
                    
                    emoji = size_emoji.get(info['size'], '📋')
                    purpose_icon = purpose_emoji.get(info['purpose'], '📋')
                    
                    description = f"{purpose_icon} {info['description']} ({info['word_count']} words)"
                    options[name] = description
        
        # Add cewl-generated wordlist if available
        if self.generated_cewl_wordlist and os.path.exists(self.generated_cewl_wordlist):
            word_count = self._count_words_in_file(self.generated_cewl_wordlist)
            options['cewl_generated'] = f"🕷️ Custom CeWL wordlist ({word_count} words)"
        
        # Fallback to config wordlists if nothing detected
        if not options:
            wordlist_config = self.config.get('wordlists', {})
            for key, path in wordlist_config.items():
                if key != 'base_dir' and os.path.exists(path):
                    word_count = self._count_words_in_file(path)
                    options[key] = f"📋 {path} ({word_count} words)"
        
        return options
    
    def prompt_wordlist_selection(self, tool_name: str = "directory enumeration", scan_type: str = "directory") -> Tuple[str, str]:
        """
        Prompt user to select wordlist type with HTB-optimized recommendations
        Returns tuple of (wordlist_type, wordlist_path)
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}📚 HTB-Optimized Wordlist Selection for {tool_name.title()}{Colors.END}")
        print(f"{Colors.CYAN}═══════════════════════════════════════════════════════════════════{Colors.END}")
        
        # Show intelligent recommendation first
        rec_name, rec_path = self.get_recommended_wordlist(scan_type, 'balanced')
        if rec_name and rec_path and os.path.exists(rec_path):
            word_count = self._count_words_in_file(rec_path)
            print(f"{Colors.GREEN}🎯 RECOMMENDED for HTB: {rec_name.replace('_', ' ').title()}{Colors.END}")
            if self.detected_wordlists and rec_name in self.detected_wordlists['available_lists']:
                info = self.detected_wordlists['available_lists'][rec_name]
                print(f"{Colors.CYAN}   {info['description']}{Colors.END}")
            
            use_recommended = input(f"{Colors.YELLOW}Use recommended wordlist? (Y/n): {Colors.END}").strip().lower()
            if use_recommended in ['', 'y', 'yes']:
                print(f"{Colors.GREEN}✅ Using HTB-optimized recommendation: {word_count} words{Colors.END}")
                return rec_name, rec_path
        
        # Check if we can generate cewl wordlist
        can_generate_cewl = (
            self.check_cewl_available() and 
            (self.discovered_domains or self.web_ports)
        )
        
        if can_generate_cewl and not self.generated_cewl_wordlist:
            print(f"\n{Colors.GREEN}🕷️  CeWL is available and web content detected!{Colors.END}")
            print(f"{Colors.CYAN}💡 CeWL can generate a custom wordlist from the target website{Colors.END}")
            
            # Offer to generate cewl wordlist
            while True:
                choice = input(f"\n{Colors.YELLOW}Generate custom wordlist with CeWL? (y/N/d for diagnostics): {Colors.END}").strip().lower()
                
                if choice in ['y', 'yes']:
                    # Determine best target URL for cewl
                    target_url = self._get_best_cewl_target()
                    if target_url:
                        cewl_path = self.generate_cewl_wordlist(target_url)
                        if cewl_path:
                            print(f"{Colors.GREEN}✨ Using CeWL-generated wordlist for {tool_name}{Colors.END}")
                            return 'cewl_generated', cewl_path
                        else:
                            print(f"{Colors.YELLOW}⚠️  CeWL generation failed{Colors.END}")
                            # Offer diagnostics when CeWL fails
                            diag_choice = input(f"{Colors.CYAN}Run CeWL diagnostics to troubleshoot? (y/N): {Colors.END}").strip().lower()
                            if diag_choice in ['y', 'yes']:
                                self.diagnose_cewl_issues(target_url)
                            print(f"{Colors.CYAN}Falling back to standard wordlist options...{Colors.END}")
                    break
                elif choice in ['d', 'diag', 'diagnostics']:
                    # Run diagnostics
                    target_url = self._get_best_cewl_target()
                    self.diagnose_cewl_issues(target_url)
                    continue  # Stay in the loop
                elif choice in ['n', 'no', '']:
                    break
                else:
                    print(f"{Colors.RED}Please enter 'y', 'n', or 'd' for diagnostics{Colors.END}")
        
        # Show available wordlist options
        options = self.get_wordlist_options()
        
        if not options:
            print(f"{Colors.YELLOW}⚠️  No wordlists found, will create minimal fallback{Colors.END}")
            minimal_path = self._create_minimal_wordlist()
            if minimal_path:
                return 'minimal', minimal_path
            else:
                print(f"{Colors.RED}❌ Cannot create minimal wordlist fallback{Colors.END}")
                raise Exception("No wordlists available and cannot create fallback")
        
        print(f"\n{Colors.BOLD}Available HTB-Optimized Wordlists:{Colors.END}")
        
        # Create numbered menu with intelligent categorization
        option_keys = list(options.keys())
        
        # Group by type for better display
        htb_lists = [k for k in option_keys if k.startswith('htb_')]
        classic_lists = [k for k in option_keys if k.startswith(('dirb_', 'dirbuster_'))]
        other_lists = [k for k in option_keys if not k.startswith(('htb_', 'dirb_', 'dirbuster_', 'cewl_'))]
        cewl_lists = [k for k in option_keys if k.startswith('cewl_')]
        
        # Display organized menu
        counter = 1
        displayed_order = []
        
        if htb_lists:
            print(f"\n{Colors.PURPLE}🎯 HTB-Optimized Wordlists:{Colors.END}")
            for key in htb_lists:
                description = options[key]
                speed_indicator = self._get_speed_indicator(key)
                print(f"  {Colors.CYAN}{counter}) {key.replace('_', ' ').title()}{Colors.END}{speed_indicator}")
                print(f"     {Colors.CYAN}{description}{Colors.END}")
                displayed_order.append(key)
                counter += 1
        
        if cewl_lists:
            print(f"\n{Colors.PURPLE}🕷️ Custom Generated:{Colors.END}")
            for key in cewl_lists:
                description = options[key]
                print(f"  {Colors.CYAN}{counter}) {key.replace('_', ' ').title()}{Colors.END} {Colors.PURPLE}(target-specific){Colors.END}")
                print(f"     {Colors.CYAN}{description}{Colors.END}")
                displayed_order.append(key)
                counter += 1
        
        if classic_lists:
            print(f"\n{Colors.BLUE}📚 Classic Wordlists:{Colors.END}")
            for key in classic_lists:
                description = options[key]
                print(f"  {Colors.CYAN}{counter}) {key.replace('_', ' ').title()}{Colors.END}")
                print(f"     {Colors.CYAN}{description}{Colors.END}")
                displayed_order.append(key)
                counter += 1
        
        if other_lists:
            print(f"\n{Colors.YELLOW}📋 Other Available:{Colors.END}")
            for key in other_lists:
                description = options[key]
                print(f"  {Colors.CYAN}{counter}) {key.replace('_', ' ').title()}{Colors.END}")
                print(f"     {Colors.CYAN}{description}{Colors.END}")
                displayed_order.append(key)
                counter += 1
        
        # Add custom wordlist option
        custom_option = counter
        print(f"\n  {Colors.CYAN}{custom_option}) Custom wordlist{Colors.END} {Colors.YELLOW}(specify path){Colors.END}")
        
        # Get user selection
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}Select wordlist (1-{custom_option}, default: 1): {Colors.END}").strip()
                
                if not choice:
                    choice = "1"
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(displayed_order):
                    selected_key = displayed_order[choice_num - 1]
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
                print(f"\n{Colors.YELLOW}⏭️  Using HTB-optimized default{Colors.END}")
                return self.get_recommended_wordlist(scan_type, 'balanced')
    
    def _get_speed_indicator(self, wordlist_name: str) -> str:
        """Get speed indicator for wordlist display"""
        if not self.detected_wordlists or wordlist_name not in self.detected_wordlists['available_lists']:
            return ""
        
        info = self.detected_wordlists['available_lists'][wordlist_name]
        speed = info.get('speed', 'balanced')
        
        indicators = {
            'lightning': f" {Colors.GREEN}(⚡ 30s){Colors.END}",
            'fast': f" {Colors.GREEN}(⚡ 2-5min){Colors.END}",
            'balanced': f" {Colors.YELLOW}(⚖️ 5-15min){Colors.END}",
            'slow': f" {Colors.RED}(🐌 15min+){Colors.END}"
        }
        
        return indicators.get(speed, "")
    
    def _get_best_cewl_target(self) -> Optional[str]:
        """Determine the best target URL for cewl generation with improved logic"""
        if not self.discovered_domains and not self.web_ports:
            print(f"{Colors.YELLOW}⚠️  No discovered domains or web ports available for CeWL{Colors.END}")
            return None
        
        if self.discovered_domains:
            # Use the first discovered domain with preferred protocol
            domain = self.discovered_domains[0].strip()
            print(f"{Colors.CYAN}🎯 Using discovered domain: {domain}{Colors.END}")
            
            # Try different URL combinations in order of preference
            url_candidates = []
            
            # HTTPS options
            for port in [443, 8443] + [p for p in self.web_ports if p in [443, 8443]]:
                if port == 443:
                    url_candidates.append(f"https://{domain}")
                else:
                    url_candidates.append(f"https://{domain}:{port}")
            
            # HTTP options
            for port in [80, 8080, 8000] + [p for p in self.web_ports if p not in [443, 8443]]:
                if port == 80:
                    url_candidates.append(f"http://{domain}")
                else:
                    url_candidates.append(f"http://{domain}:{port}")
            
            # Test URLs for accessibility (simple check)
            for url in url_candidates:
                try:
                    print(f"{Colors.CYAN}🔍 Testing URL: {url}{Colors.END}")
                    # Quick connection test could be added here
                    # For now, return the first HTTPS URL or first HTTP URL
                    if url.startswith('https://'):
                        print(f"{Colors.GREEN}✅ Selected HTTPS URL: {url}{Colors.END}")
                        return url
                except:
                    continue
            
            # Fallback to first HTTP URL
            for url in url_candidates:
                if url.startswith('http://'):
                    print(f"{Colors.YELLOW}⚠️  Falling back to HTTP URL: {url}{Colors.END}")
                    return url
        
        print(f"{Colors.RED}❌ Could not determine suitable target URL for CeWL{Colors.END}")
        return None
    
    def _get_wordlist_path_by_key(self, key: str) -> Optional[str]:
        """Get wordlist path by key"""
        if key == 'cewl_generated':
            return self.generated_cewl_wordlist
        
        # Check auto-detected wordlists first
        if self.detected_wordlists and key in self.detected_wordlists['available_lists']:
            return self.detected_wordlists['available_lists'][key]['path']
        
        # Fallback to config
        wordlist_config = self.config.get('wordlists', {})
        return wordlist_config.get(key)
    
    def _get_default_wordlist(self) -> Tuple[str, str]:
        """Get default wordlist fallback with HTB optimization"""
        # Try HTB-optimized recommendation first
        if self.detected_wordlists and self.detected_wordlists['available_lists']:
            rec_name, rec_path = self.get_recommended_wordlist('directory', 'balanced')
            if rec_name and rec_path and os.path.exists(rec_path):
                return rec_name, rec_path
        
        # Try config wordlists
        wordlist_config = self.config.get('wordlists', {})
        for key in ['common', 'small', 'ferox_small']:
            if key in wordlist_config:
                path = wordlist_config[key]
                if os.path.exists(path):
                    return key, path
        
        # Last resort - create minimal wordlist
        minimal_path = self._create_minimal_wordlist()
        if minimal_path:
            return 'minimal', minimal_path
        else:
            # Absolute fallback - return None to indicate no wordlist available
            print(f"{Colors.RED}❌ Unable to create any wordlist fallback{Colors.END}")
            return None, None
    
    def _create_minimal_wordlist(self) -> str:
        """Create a minimal HTB-optimized wordlist as fallback"""
        # HTB-optimized minimal wordlist based on common findings
        minimal_words = [
            'admin', 'login', 'index', 'home', 'test', 'backup', 'config', 'data',
            'api', 'upload', 'download', 'files', 'images', 'js', 'css', 'assets',
            'static', 'robots.txt', 'sitemap.xml', 'favicon.ico', '.htaccess',
            'phpmyadmin', 'wp-admin', 'administrator', 'panel', 'dashboard',
            # HTB-specific additions
            'htb', 'hackthebox', 'flag', 'user', 'root', 'dev', 'development',
            'staging', 'prod', 'production', 'secure', 'private', 'internal',
            'secret', 'hidden', 'temp', 'tmp', 'logs', 'log', 'debug',
            'console', 'terminal', 'shell', 'cmd', 'exec', 'system'
        ]
        
        minimal_path = os.path.join(self.output_dir, 'htb_minimal_wordlist.txt')
        
        try:
            with open(minimal_path, 'w') as f:
                f.write('\n'.join(minimal_words))
            
            print(f"{Colors.YELLOW}⚠️  Created HTB-optimized minimal wordlist: {minimal_path}{Colors.END}")
            return minimal_path
        
        except Exception as e:
            print(f"{Colors.RED}❌ Error creating minimal wordlist: {str(e)}{Colors.END}")
            return None
    
    def cleanup_generated_wordlists(self):
        """Clean up generated wordlists at the end of scanning"""
        if self.generated_cewl_wordlist and os.path.exists(self.generated_cewl_wordlist):
            print(f"{Colors.CYAN}🧹 Keeping CeWL-generated wordlist: {self.generated_cewl_wordlist}{Colors.END}")
            print(f"{Colors.CYAN}💡 You can reuse this wordlist for future scans of the same target{Colors.END}")
    
    def _analyze_wordlist_directory_structure(self, base_path: str) -> Dict[str, Dict]:
        """Recursively analyze wordlist directory structure and categorize by content"""
        analysis = {}
        
        if not os.path.exists(base_path):
            return analysis
        
        try:
            # Use os.walk to recursively scan directories
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith(('.txt', '.list', '.wordlist')):
                        file_path = os.path.join(root, file)
                        
                        # Extract relative path for categorization
                        rel_path = os.path.relpath(file_path, base_path)
                        path_parts = rel_path.split(os.sep)
                        
                        # Analyze file metadata
                        try:
                            file_stats = os.stat(file_path)
                            file_size = file_stats.st_size
                            word_count = self._count_words_in_file(file_path)
                            
                            # Skip empty or very small files
                            if word_count < 10:
                                continue
                            
                            # Categorize by directory structure and filename
                            category = self._categorize_by_path_and_name(path_parts, file)
                            
                            # Determine size category
                            size_category = self._determine_size_category(word_count, file_size)
                            
                            # Estimate scan time
                            estimated_time = self._estimate_scan_time(word_count)
                            
                            # Create wordlist entry
                            key = self._generate_wordlist_key(path_parts, file)
                            
                            analysis[key] = {
                                'path': file_path,
                                'description': self._generate_description(path_parts, file, word_count),
                                'purpose': category['purpose'],
                                'size': size_category,
                                'speed': category['speed'],
                                'word_count': word_count,
                                'file_size': file_size,
                                'estimated_time': estimated_time,
                                'source_dir': '/'.join(path_parts[:-1]) if len(path_parts) > 1 else '',
                                'quality_score': self._calculate_quality_score(path_parts, file, word_count)
                            }
                            
                        except (OSError, PermissionError) as e:
                            continue
                            
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Error analyzing directory {base_path}: {str(e)}{Colors.END}")
            
        return analysis
    
    def _categorize_by_path_and_name(self, path_parts: List[str], filename: str) -> Dict[str, str]:
        """Categorize wordlist based on path structure and filename"""
        path_str = '/'.join(path_parts).lower()
        filename_lower = filename.lower()
        
        # Purpose detection based on path and filename
        if any(keyword in path_str for keyword in ['dns', 'subdomain', 'vhost']):
            purpose = 'subdomain'
            speed = 'balanced'
        elif any(keyword in path_str for keyword in ['api', 'endpoint']):
            purpose = 'api'
            speed = 'fast'
        elif any(keyword in filename_lower for keyword in ['file', 'backup', 'config']):
            purpose = 'files'
            speed = 'balanced'
        elif any(keyword in path_str for keyword in ['web-content', 'directory', 'dir']):
            purpose = 'directory'
            speed = 'balanced'
        elif any(keyword in filename_lower for keyword in ['param', 'parameter']):
            purpose = 'parameter'
            speed = 'fast'
        else:
            purpose = 'directory'  # Default
            speed = 'balanced'
            
        # Speed adjustment based on common patterns
        if any(keyword in filename_lower for keyword in ['small', 'common', 'short', 'top100', 'top1000']):
            speed = 'lightning'
        elif any(keyword in filename_lower for keyword in ['big', 'large', 'huge', 'comprehensive', 'top100000']):
            speed = 'slow'
        elif any(keyword in filename_lower for keyword in ['medium', 'balanced']):
            speed = 'fast'
            
        return {'purpose': purpose, 'speed': speed}
    
    def _determine_size_category(self, word_count: int, file_size: int) -> str:
        """Determine size category based on word count and file size"""
        if word_count <= 1000:
            return 'small'
        elif word_count <= 50000:
            return 'medium'
        else:
            return 'large'
    
    def _estimate_scan_time(self, word_count: int) -> str:
        """Estimate scan time based on word count"""
        # Rough estimates for directory scanning (varies by target)
        if word_count <= 500:
            return "30s-1min"
        elif word_count <= 2000:
            return "1-3min"
        elif word_count <= 10000:
            return "3-10min"
        elif word_count <= 50000:
            return "10-30min"
        else:
            return "30min+"
    
    def _generate_wordlist_key(self, path_parts: List[str], filename: str) -> str:
        """Generate a unique key for the wordlist"""
        # Create a meaningful key from path and filename
        if len(path_parts) > 1:
            category = path_parts[-2].lower().replace('-', '_').replace(' ', '_')
            name = os.path.splitext(filename)[0].lower().replace('-', '_').replace(' ', '_')
            return f"{category}_{name}"
        else:
            return os.path.splitext(filename)[0].lower().replace('-', '_').replace(' ', '_')
    
    def _generate_description(self, path_parts: List[str], filename: str, word_count: int) -> str:
        """Generate a human-readable description for the wordlist"""
        category = path_parts[-2] if len(path_parts) > 1 else "General"
        name = os.path.splitext(filename)[0]
        
        # Create descriptive text
        if 'dns' in category.lower() or 'subdomain' in filename.lower():
            return f"Subdomain enumeration - {name} ({word_count:,} entries)"
        elif 'api' in category.lower() or 'api' in filename.lower():
            return f"API endpoint discovery - {name} ({word_count:,} entries)"
        elif 'web-content' in category.lower():
            return f"Web directory discovery - {name} ({word_count:,} entries)"
        else:
            return f"{category} wordlist - {name} ({word_count:,} entries)"
    
    def _calculate_quality_score(self, path_parts: List[str], filename: str, word_count: int) -> float:
        """Calculate a quality score for wordlist ranking"""
        score = 0.0
        
        # Base score for word count (balanced is better)
        if 1000 <= word_count <= 10000:
            score += 3.0
        elif 100 <= word_count < 1000 or 10000 < word_count <= 50000:
            score += 2.0
        else:
            score += 1.0
        
        # Bonus for well-known, quality wordlists
        filename_lower = filename.lower()
        path_str = '/'.join(path_parts).lower()
        
        if any(keyword in filename_lower for keyword in ['directory-list', 'common', 'raft']):
            score += 2.0
        if 'seclists' in path_str:
            score += 1.5
        if any(keyword in filename_lower for keyword in ['medium', 'balanced']):
            score += 1.0
        if any(keyword in path_str for keyword in ['discovery', 'web-content']):
            score += 1.0
            
        # Penalty for very large or very small lists
        if word_count > 100000 or word_count < 50:
            score -= 1.0
            
        return score
    
    def get_wordlists_by_purpose(self, purpose: str) -> Dict[str, Dict]:
        """Get all wordlists filtered by purpose"""
        if not self.detected_wordlists or not self.detected_wordlists['available_lists']:
            return {}
            
        return {
            name: info for name, info in self.detected_wordlists['available_lists'].items()
            if info.get('purpose', 'directory') == purpose
        }
    
    def get_top_wordlists(self, purpose: str = None, limit: int = 5) -> List[Tuple[str, Dict]]:
        """Get top wordlists by quality score, optionally filtered by purpose"""
        if not self.detected_wordlists or not self.detected_wordlists['available_lists']:
            return []
        
        available = self.detected_wordlists['available_lists']
        
        # Filter by purpose if specified
        if purpose:
            available = {
                name: info for name, info in available.items()
                if info.get('purpose', 'directory') == purpose
            }
        
        # Sort by quality score and return top N
        sorted_wordlists = sorted(
            available.items(),
            key=lambda x: x[1].get('quality_score', 0),
            reverse=True
        )
        
        return sorted_wordlists[:limit]
    
    def get_context_aware_recommendation(self, scan_type: str = 'directory', target_info: Dict = None) -> Tuple[str, str]:
        """Get context-aware wordlist recommendation based on target analysis"""
        if not target_info:
            target_info = {}
        
        # Extract context information
        web_technologies = target_info.get('web_technologies', [])
        open_ports = target_info.get('open_ports', [])
        server_headers = target_info.get('server_headers', {})
        cms_detected = target_info.get('cms', '')
        target_os = target_info.get('os', '')
        
        print(f"{Colors.CYAN}🧠 Analyzing target context for intelligent wordlist selection...{Colors.END}")
        
        # Context-based scoring adjustments
        context_adjustments = {}
        
        # CMS-specific adjustments
        if cms_detected:
            cms_lower = cms_detected.lower()
            if 'wordpress' in cms_lower:
                context_adjustments['wordpress'] = 2.0
                context_adjustments['wp'] = 2.0
                context_adjustments['admin'] = 1.5
            elif 'drupal' in cms_lower:
                context_adjustments['drupal'] = 2.0
                context_adjustments['admin'] = 1.5
            elif 'joomla' in cms_lower:
                context_adjustments['joomla'] = 2.0
                context_adjustments['administrator'] = 1.5
        
        # Technology-specific adjustments
        for tech in web_technologies:
            tech_lower = tech.lower()
            if 'php' in tech_lower:
                context_adjustments['php'] = 1.5
                context_adjustments['config'] = 1.3
            elif 'asp' in tech_lower or 'iis' in tech_lower:
                context_adjustments['aspx'] = 1.5
                context_adjustments['asp'] = 1.5
            elif 'apache' in tech_lower:
                context_adjustments['apache'] = 1.3
                context_adjustments['htaccess'] = 1.5
            elif 'nginx' in tech_lower:
                context_adjustments['nginx'] = 1.3
            elif 'tomcat' in tech_lower:
                context_adjustments['tomcat'] = 1.5
                context_adjustments['manager'] = 1.5
        
        # Port-based adjustments
        if 8080 in open_ports:
            context_adjustments['tomcat'] = 1.5
            context_adjustments['manager'] = 1.5
        if 3000 in open_ports:
            context_adjustments['node'] = 1.5
            context_adjustments['api'] = 1.3
        if 8000 in open_ports or 8001 in open_ports:
            context_adjustments['api'] = 1.5
            context_adjustments['dev'] = 1.3
        
        # Server header-based adjustments
        server = server_headers.get('server', '').lower()
        if 'apache' in server:
            context_adjustments['apache'] = 1.3
        elif 'nginx' in server:
            context_adjustments['nginx'] = 1.3
        elif 'iis' in server:
            context_adjustments['iis'] = 1.3
            context_adjustments['aspx'] = 1.5
        
        # OS-based adjustments
        if target_os:
            os_lower = target_os.lower()
            if 'windows' in os_lower:
                context_adjustments['windows'] = 1.3
                context_adjustments['aspx'] = 1.2
            elif 'linux' in os_lower:
                context_adjustments['php'] = 1.2
                context_adjustments['apache'] = 1.2
        
        # Get base recommendation
        base_name, base_path = self.get_recommended_wordlist(scan_type, 'balanced')
        
        # If we have context adjustments, try to find a better match
        if context_adjustments and self.detected_wordlists:
            available = self.detected_wordlists.get('available_lists', {})
            
            # Calculate context-adjusted scores
            scored_wordlists = []
            for name, info in available.items():
                if info.get('purpose', 'directory') == scan_type or scan_type == 'directory':
                    base_score = info.get('quality_score', 0)
                    context_score = 0
                    
                    # Apply context adjustments based on filename and path
                    full_path = info.get('path', '').lower()
                    name_lower = name.lower()
                    
                    for keyword, bonus in context_adjustments.items():
                        if keyword in full_path or keyword in name_lower:
                            context_score += bonus
                    
                    total_score = base_score + context_score
                    scored_wordlists.append((name, info, total_score))
            
            # Sort by total score and get the best match
            if scored_wordlists:
                best_match = max(scored_wordlists, key=lambda x: x[2])
                if best_match[2] > 0:  # Only use if we got some context bonus
                    print(f"{Colors.GREEN}🎯 Context-aware selection: {best_match[0]} (score: {best_match[2]:.1f}){Colors.END}")
                    return best_match[0], best_match[1]['path']
        
        print(f"{Colors.YELLOW}📋 Using base recommendation: {base_name}{Colors.END}")
        return base_name, base_path
    
    def analyze_target_for_wordlist_hints(self, nmap_results: str = "", web_scan_results: str = "") -> Dict:
        """Analyze scan results to extract hints for better wordlist selection"""
        hints = {
            'web_technologies': [],
            'cms': '',
            'server_headers': {},
            'interesting_paths': [],
            'potential_admin_paths': []
        }
        
        # Analyze nmap results for service detection
        if nmap_results:
            lines = nmap_results.split('\n')
            for line in lines:
                line_lower = line.lower()
                
                # Look for web technologies
                if 'http' in line_lower:
                    if 'apache' in line_lower:
                        hints['web_technologies'].append('Apache')
                    if 'nginx' in line_lower:
                        hints['web_technologies'].append('Nginx')
                    if 'iis' in line_lower:
                        hints['web_technologies'].append('IIS')
                    if 'php' in line_lower:
                        hints['web_technologies'].append('PHP')
                    if 'asp' in line_lower:
                        hints['web_technologies'].append('ASP')
                    if 'tomcat' in line_lower:
                        hints['web_technologies'].append('Tomcat')
                
                # Look for CMS indicators
                if 'wordpress' in line_lower or 'wp-' in line_lower:
                    hints['cms'] = 'WordPress'
                elif 'drupal' in line_lower:
                    hints['cms'] = 'Drupal'
                elif 'joomla' in line_lower:
                    hints['cms'] = 'Joomla'
        
        # Analyze web scan results
        if web_scan_results:
            lines = web_scan_results.split('\n')
            for line in lines:
                line_lower = line.lower()
                
                # Look for admin panels
                if any(admin_term in line_lower for admin_term in ['admin', 'login', 'panel', 'dashboard']):
                    if 'http' in line_lower or '200' in line or '302' in line:
                        hints['potential_admin_paths'].append(line.strip())
                
                # Look for interesting file extensions
                if any(ext in line_lower for ext in ['.php', '.asp', '.jsp', '.py']):
                    hints['interesting_paths'].append(line.strip())
        
        return hints 
    
    def diagnose_cewl_issues(self, target_url: str = None) -> Dict[str, bool]:
        """Comprehensive diagnostic function for CeWL troubleshooting"""
        print(f"{Colors.CYAN}🔧 Running CeWL diagnostic suite...{Colors.END}")
        
        diagnostic_results = {
            'cewl_installed': False,
            'cewl_version': '',
            'output_dir_writable': False,
            'network_connectivity': False,
            'target_accessible': False,
            'ruby_available': False
        }
        
        # Test 1: CeWL Installation
        print(f"{Colors.CYAN}1️⃣  Testing CeWL installation...{Colors.END}")
        try:
            result = subprocess.run(['cewl', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                diagnostic_results['cewl_installed'] = True
                version_info = result.stdout.strip() or result.stderr.strip()
                diagnostic_results['cewl_version'] = version_info
                print(f"{Colors.GREEN}   ✅ CeWL installed: {version_info}{Colors.END}")
            else:
                print(f"{Colors.RED}   ❌ CeWL not responding to --version{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}   ❌ CeWL not found: {str(e)}{Colors.END}")
            # Check if Ruby is available (CeWL dependency)
            try:
                ruby_result = subprocess.run(['ruby', '--version'], capture_output=True, text=True, timeout=5)
                if ruby_result.returncode == 0:
                    diagnostic_results['ruby_available'] = True
                    print(f"{Colors.YELLOW}   ⚠️  Ruby available: {ruby_result.stdout.strip()}{Colors.END}")
                    print(f"{Colors.CYAN}   💡 Try installing CeWL with: gem install cewl{Colors.END}")
                else:
                    print(f"{Colors.RED}   ❌ Ruby not available{Colors.END}")
            except:
                print(f"{Colors.RED}   ❌ Ruby not found{Colors.END}")
        
        # Test 2: Output Directory
        print(f"{Colors.CYAN}2️⃣  Testing output directory permissions...{Colors.END}")
        try:
            test_file = os.path.join(self.output_dir, 'cewl_test.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            diagnostic_results['output_dir_writable'] = True
            print(f"{Colors.GREEN}   ✅ Output directory writable: {self.output_dir}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}   ❌ Cannot write to output directory: {str(e)}{Colors.END}")
            print(f"{Colors.CYAN}   💡 Check permissions for: {self.output_dir}{Colors.END}")
        
        # Test 3: Network Connectivity
        print(f"{Colors.CYAN}3️⃣  Testing network connectivity...{Colors.END}")
        try:
            import urllib.request
            with urllib.request.urlopen('https://www.google.com', timeout=10) as response:
                if response.status == 200:
                    diagnostic_results['network_connectivity'] = True
                    print(f"{Colors.GREEN}   ✅ Internet connectivity working{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}   ❌ Network connectivity issue: {str(e)}{Colors.END}")
        
        # Test 4: Target URL Accessibility (if provided)
        if target_url:
            print(f"{Colors.CYAN}4️⃣  Testing target URL accessibility...{Colors.END}")
            try:
                import urllib.request
                request = urllib.request.Request(target_url, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; CeWL-Diagnostic)'
                })
                with urllib.request.urlopen(request, timeout=15) as response:
                    if response.status == 200:
                        diagnostic_results['target_accessible'] = True
                        content_type = response.headers.get('content-type', '')
                        print(f"{Colors.GREEN}   ✅ Target accessible: {target_url}{Colors.END}")
                        print(f"{Colors.GREEN}   📄 Content-Type: {content_type}{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}   ⚠️  Target responded with status: {response.status}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}   ❌ Target not accessible: {str(e)}{Colors.END}")
                print(f"{Colors.CYAN}   💡 Try testing with curl: curl -I {target_url}{Colors.END}")
        
        # Summary
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 Diagnostic Summary:{Colors.END}")
        total_tests = len(diagnostic_results)
        passed_tests = sum(diagnostic_results.values())
        
        for test, result in diagnostic_results.items():
            status = f"{Colors.GREEN}✅" if result else f"{Colors.RED}❌"
            print(f"   {status} {test.replace('_', ' ').title()}{Colors.END}")
        
        print(f"\n{Colors.CYAN}📊 Tests passed: {passed_tests}/{total_tests}{Colors.END}")
        
        if not diagnostic_results['cewl_installed']:
            print(f"\n{Colors.YELLOW}💡 CeWL Installation Instructions:{Colors.END}")
            print(f"{Colors.CYAN}   • Ubuntu/Debian: sudo apt install cewl{Colors.END}")
            print(f"{Colors.CYAN}   • Ruby Gem: gem install cewl{Colors.END}")
            print(f"{Colors.CYAN}   • Kali Linux: Already included in most distributions{Colors.END}")
        
        return diagnostic_results 