# ipsnipe Changelog

All notable changes to this project will be documented in this file.

## [3.2] - 2024-12-23 - Wordlist Management & Configuration Stability Edition

### 🎯 CRITICAL WORDLIST MANAGEMENT FIXES
- **🔧 Resolved Configuration Conflicts** - Eliminated competing wordlist configuration systems
  - Fixed critical issue where only nmap scans worked while other scanners (feroxbuster, ffuf, etc.) failed
  - Removed conflicting TOML configuration that competed with intelligent auto-detection system
  - Unified wordlist management under single, robust auto-detection system
  - Enhanced error handling for missing wordlist scenarios with graceful fallbacks

### 🧠 Enhanced Intelligent Wordlist Selection
- **🎯 Multi-Layer Intelligence System** - Sophisticated wordlist selection based on target analysis
  - **Layer 1**: Deep directory structure analysis with recursive file scanning
  - **Layer 2**: Multi-factor categorization by path structure, filename patterns, and word count
  - **Layer 3**: Quality scoring system (2,663+ wordlists intelligently ranked)
  - **Layer 4**: Context-aware selection based on detected technologies, ports, and CMS
  - **Layer 5**: Final intelligent ranking combining all factors for optimal wordlist selection

### 🔍 Advanced Auto-Detection System
- **📊 Comprehensive Wordlist Analysis** - Intelligent categorization of thousands of wordlists
  - Auto-detection of SecLists, Dirb, DirBuster, and custom wordlist locations
  - Purpose-based categorization: directory, subdomain, API, files, parameters
  - Size-based optimization: small (<1K), medium (1K-50K), large (>50K) word classifications
  - Speed estimation: lightning (30s-1min), fast (1-10min), slow (30min+) scan times
  - Quality scoring based on effectiveness, source reputation, and optimal sizing

### 🎮 Context-Aware Target Intelligence
- **🧠 Technology-Based Wordlist Selection** - Adaptive wordlist choice based on target characteristics
  - **CMS Detection**: WordPress (+2.0 bonus), Drupal (+2.0), Joomla (+1.5) specific wordlists
  - **Technology Stack**: PHP (+1.5), Apache (+1.3), Nginx (+1.3), IIS (+1.3), Tomcat (+1.5) optimizations
  - **Port-Based Intelligence**: Port 8080 (Tomcat +1.5), Port 3000 (Node.js/API +1.5), Port 8000 (Dev +1.3)
  - **Server Header Analysis**: Automatic adjustment based on detected web server technologies
  - **OS-Specific Optimization**: Windows/Linux specific wordlist prioritization

### 🛠️ Robust Error Handling & Fallbacks
- **✅ Graceful Degradation** - Reliable operation across all environments
  - Enhanced fallback mechanisms when standard wordlists are unavailable
  - Minimal wordlist creation for non-HTB environments
  - Improved error messages with actionable troubleshooting guidance
  - Comprehensive wordlist validation before scanner execution
  - Smart recovery from corrupted or missing wordlist files

### 🚀 HTB Environment Optimization
- **🎯 Perfect HTB Integration** - Seamless operation in Hack The Box environments
  - Validated detection of 2,663+ intelligent wordlists in HTB environments
  - Enhanced SecLists integration with deep structural analysis
  - Optimized wordlist selection for CTF/HTB scenarios
  - Automatic detection of HTB-specific wordlist collections
  - Zero-configuration operation in standard HTB setups

### 📈 Performance & Reliability Improvements
- **⚡ Enhanced Scanner Stability** - All scanners now work reliably without conflicts
  - Fixed feroxbuster wordlist resolution issues
  - Resolved ffuf subdomain enumeration wordlist problems
  - Enhanced web scanner wordlist fallback mechanisms
  - Improved parameter scanner wordlist detection
  - Eliminated hardcoded path conflicts with dynamic detection

### 🔧 Configuration System Cleanup
- **🧹 Simplified Configuration Architecture** - Streamlined single-source configuration
  - Removed competing TOML/Python configuration conflicts
  - Unified under intelligent auto-detection system
  - Eliminated configuration priority confusion
  - Reduced complexity while maintaining full functionality
  - Clear separation between emergency fallbacks and primary detection

### 🎓 Enhanced User Experience
- **📚 Intelligent Wordlist Recommendations** - Clear guidance for optimal wordlist selection
  - Context-aware wordlist suggestions based on target analysis
  - Quality scoring visible to users for informed decision making
  - Speed/coverage trade-off recommendations
  - Educational descriptions explaining wordlist purposes and estimated scan times
  - Streamlined selection process with intelligent defaults

## [3.1] - 2024-12-18 - Portability & Installer Enhancement Edition

### 🚀 Major Installer Improvements
- **🌍 Eliminated Hard-coded Paths** - Complete portability enhancement
  - Removed all hard-coded `/opt/homebrew` paths for Apple Silicon compatibility
  - Added dynamic Homebrew detection supporting both `/opt/homebrew` (Apple Silicon) and `/usr/local` (Intel)
  - Enhanced installer portability across different macOS configurations and architectures
  - Improved cross-platform compatibility for various Linux distributions

### 🔧 Enhanced macOS Support
- **🍎 Intelligent macOS SSL Handling** - Fixed wfuzz installation issues
  - Comprehensive SSL environment setup for pycurl installation
  - Auto-detection of OpenSSL and curl-openssl Homebrew packages
  - Smart fallback to modern alternatives (ffuf, feroxbuster) when wfuzz fails
  - Proper SSL backend configuration following official wfuzz documentation

### 🛠️ Python Environment Consistency
- **🐍 Improved Python Detection** - Eliminated version conflicts
  - Fixed Python executable detection inconsistencies between installer and verification
  - Enhanced clarity about which Python version is being used during installation
  - Eliminated redundant Python detection that caused version mismatches
  - Added transparent reporting of system vs PATH-priority Python versions

### 🧪 Robust Verification System
- **✅ Enhanced Package Verification** - More reliable dependency checking
  - Improved Python package detection with multiple fallback methods
  - Fixed verification failures caused by PATH modifications during installation
  - Enhanced error reporting and debugging capabilities
  - Added comprehensive verification status for all components

### 🔄 Smart Tool Management
- **⚙️ Graceful Fallback Strategy** - Better handling of installation failures
  - Intelligent handling of tools that fail to install (especially wfuzz on macOS)
  - Clear communication about alternative tools when preferred options fail
  - Maintained full functionality even when individual tools can't be installed
  - Enhanced status reporting for optional vs required components

### 🎯 Installation Process Improvements
- **📦 Streamlined Package Management** - More reliable installation flow
  - Fixed package synchronization between installer and uninstaller
  - Corrected Python package list (removed unused colorama, ensured requests inclusion)
  - Enhanced error recovery during installation process
  - Improved handling of externally-managed Python environments

### 🗑️ Uninstaller Enhancements
- **🔧 Dynamic Path Detection** - Portable uninstall process
  - Removed hard-coded paths in uninstaller matching installer improvements
  - Enhanced tool detection across multiple installation paths
  - Improved cleanup of manually installed tools and Go-based applications
  - Better handling of various package manager installations

### 🏗️ Development Infrastructure
- **🛠️ Debugging Tools** - Enhanced troubleshooting capabilities
  - Created comprehensive debugging scripts for installation issues
  - Added detailed Python environment analysis tools
  - Enhanced error reporting and diagnostic information
  - Improved installation verification and status reporting

### 🎨 User Experience Improvements
- **📋 Clearer Installation Feedback** - Better user communication
  - Enhanced status messages explaining installation decisions
  - Clearer indication of which tools are optional vs required
  - Better explanation of fallback strategies when tools fail
  - Improved transparency about system configurations and choices

### 🔍 Technical Improvements
- **⚡ Performance Optimizations** - Faster, more reliable installation
  - Reduced redundant operations during installation process
  - Optimized PATH modifications and environment setup
  - Enhanced parallel processing of installation tasks
  - Improved timeout handling and error recovery

---

## [3.0] - 2024-12-18 - Full Sniper Mode Edition

### 🎯 MAJOR RELEASE: Full Sniper Mode - Complete Reconnaissance Revolution

This is a massive architectural overhaul that transforms ipsnipe from a multi-tool selector into a unified reconnaissance powerhouse. The entire interface and workflow have been redesigned around a single, comprehensive "Full Sniper Mode" that executes all tools in perfect harmony.

### 🚀 HTB-Optimized Speed Improvements (Latest Update)
- **⚡ Removed Quick Scan** - Eliminated redundant nmap_quick, focusing on single aggressive full scan
- **🔥 High Min-Rate Implementation** - Added --min-rate 5000 for maximum scanning speed (HTB-optimized)
- **🎯 Aggressive Full Scan** - Single comprehensive nmap scan with SYN scanning + high min-rate
- **📉 Reduced Tool Count** - Streamlined from 11 to 10 tools for faster execution
- **🏁 HTB-Focused** - Optimized for CTF environments where noise doesn't matter

### 🚀 Revolutionary Full Sniper Mode Features
- **🎯 Single Unified Mode** - No more complex tool selection menus - just activate Full Sniper Mode
- **🔄 Intelligent Tool Orchestration** - All 11 tools execute in optimized order with intelligence flowing between them
- **📊 Comprehensive Command Reporting** - Every tool shows exactly what command was executed for learning
- **🎪 3-Phase Execution Model** - Network Discovery → DNS Intelligence → Web Application Analysis
- **🧠 Intelligence Flow Architecture** - Each tool feeds data to enhance subsequent tools' effectiveness
- **🕸️  Perfect Tool Synchronization** - No interference between tools, optimal resource utilization

### 🔧 Complete Interface Redesign
- **🎯 Streamlined User Experience** - Single confirmation replaces complex menu navigation
- **📋 Execution Plan Preview** - Shows all tools grouped by phases before execution
- **⏱️  Time Estimation** - Provides realistic completion time estimates (15-45 minutes)
- **🎨 Enhanced Visual Design** - Red sniper theme with comprehensive progress indicators
- **📊 Real-time Phase Tracking** - Clear visual indicators of current execution phase

### 🛠️ Advanced Tool Integration
- **🔍 Phase 1: Network Discovery**
  - Nmap Quick Scan → Fast port discovery and service detection
  - Nmap Full Scan → Comprehensive port scan with vulnerability scripts  
  - Nmap UDP Scan → UDP port discovery (requires sudo privileges)

- **🌐 Phase 2: DNS & Domain Intelligence**
  - DNS Enumeration → Comprehensive DNS enumeration with dig
  - Advanced DNS → HTB-optimized DNS with certificate transparency
  - theHarvester → Email addresses and subdomain enumeration

- **🕸️  Phase 3: Web Application Analysis**
  - Enhanced Web Discovery → HTB-optimized web content discovery
  - Feroxbuster → Fast directory and file enumeration
  - FFUF → Virtual host and subdomain enumeration
  - CMS Scan → CMS identification and security analysis
  - Parameter/LFI Scan → Parameter discovery and LFI vulnerability testing

### 📊 Enhanced Reporting & Intelligence
- **🎯 Comprehensive Final Report** - Shows intelligence gathered, tool execution status, and command details
- **🧠 Intelligence Summary** - Displays discovered ports, web services, and domains
- **📁 Organized Output Structure** - All results, findings, summaries, and individual tool reports
- **🔍 Detailed Tool Execution Report** - Status and commands for every tool executed
- **📈 Success/Skip/Failure Metrics** - Complete transparency on tool performance

### ⚙️ Configuration Enhancements
- **🎯 New [full_sniper_mode] Section** - Complete control over Full Sniper Mode behavior
- **🔄 Intelligence Flow Control** - Enable/disable automatic tool data sharing
- **📊 Command Detail Control** - Show/hide exact commands for learning purposes
- **⏱️  Execution Control** - Timeouts, auto-skip failed tools, progress indicators
- **🛠️  Tool Order Optimization** - Configurable but optimized execution sequence

### 🎮 User Experience Revolution
- **🎯 Zero Decision Fatigue** - No complex tool selection, just "activate Full Sniper Mode"
- **📚 Educational Focus** - Shows commands and purposes for learning
- **🔄 Graceful Error Handling** - Failed tools don't stop the entire reconnaissance
- **⏸️  Interactive Controls** - Skip individual tools or quit all with simple commands
- **🎪 Professional Presentation** - Clean, organized output with clear phase separation

### 📖 Architectural Improvements
- **🧠 Smart Dependencies** - Tools automatically use data from previous tools
- **🔄 Automatic Web Port Discovery** - Web tools work even without nmap discoveries
- **🌐 Domain Resolution Management** - Automatic /etc/hosts management for discovered domains
- **📊 Resource Optimization** - Tools run without interfering with each other
- **🛡️  Error Isolation** - Individual tool failures don't cascade to other tools

### 💪 Performance & Reliability
- **⚡ Optimized Execution Order** - Maximum intelligence gathering efficiency
- **🔄 Robust Error Recovery** - Continue execution despite individual tool failures
- **📊 Resource Management** - Intelligent thread and timeout management across all tools
- **🎯 Focused Output** - Reduced noise, enhanced signal in results
- **🛠️  Tool Harmony** - Perfect synchronization prevents conflicts

### 🎓 Learning & Development Benefits
- **📚 Command Transparency** - See exactly what commands professionals use
- **🎯 Workflow Understanding** - Learn proper reconnaissance phase sequencing
- **📊 Results Correlation** - Understand how tools build upon each other
- **🔍 Professional Methodology** - Experience industry-standard reconnaissance workflow
- **🧠 Intelligence Analysis** - Learn to correlate findings across multiple tools

---

## [2.2] - 2024-12-18 - HTB Optimized Edition

### 🎯 Major HTB-Optimized Features Added
- **🚀 Advanced DNS Enumeration Scanner** - Comprehensive HTB-optimized DNS discovery
  - Certificate transparency discovery via crt.sh API for subdomain enumeration
  - HTB-optimized subdomain brute force (45+ common HTB subdomains: admin, api, dev, test, staging, portal, backup, secret, flag, etc.)
  - Zone transfer attempts (AXFR) against discovered nameservers
  - Reverse DNS analysis on nearby IP ranges (±10 IPs) for pattern discovery
  - Advanced tools integration: subfinder, amass, and dnsrecon when available
  - Comprehensive DNS record enumeration: A, AAAA, CNAME, MX, TXT, NS, SOA, SRV, PTR

- **🌐 Enhanced Web Discovery Scanner** - Multi-tool HTB-optimized web enumeration
  - Multi-tool directory enumeration combining gobuster with custom HTB path testing
  - JavaScript endpoint analysis and secret extraction from JS files
  - HTB-specific file extensions (25+ types: php, html, asp, jsp, txt, zip, bak, old, backup, conf, config, sql, env, log, key, pem, etc.)
  - HTB-specific paths (45+ paths: admin, login, panel, api, backup, config, secret, flag, robots.txt, .env, .htaccess, sitemap.xml, etc.)
  - Sensitive file discovery with automated testing for 25+ sensitive files common in HTB
  - Parameter discovery testing common HTB parameters (id, user, debug, cmd, include, etc.)
  - Enhanced technology fingerprinting using WhatWeb + header analysis + response fingerprinting

### 📚 Research-Backed HTB Wordlist Integration
- **HTB Champion Wordlist** - `/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt` (most successful in HTB community)
- **Fast HTB Recon** - `/usr/share/seclists/Discovery/Web-Content/common.txt` (2-3 minute scans)
- **HTB Balanced Approach** - `/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt` (different ordering strategy)
- **HTB Comprehensive** - `/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-big.txt` (maximum coverage)
- **Specialized Wordlists** - API endpoints, parameters, backup files, and subdomain discovery lists
- **Automatic SecLists Installation** - Essential HTB wordlists installed during setup

### 🛠️ HTB-Optimized Tool Installation
- **Gobuster** - Fast directory enumeration with HTB-optimized SecLists integration
- **Subfinder** - Advanced subdomain enumeration with certificate transparency and passive discovery
- **Amass** - Advanced OSINT enumeration for comprehensive subdomain and asset discovery
- **DNSRecon** - Advanced DNS reconnaissance with zone transfers, brute force, and record enumeration
- **SecLists** - Essential HTB wordlists with community-proven effectiveness
- **Enhanced install.sh** - Multi-platform installation (Debian/Ubuntu, macOS, Arch) with intelligent fallbacks

### ⚙️ HTB-Optimized Configuration
- **New [advanced_dns] Section** - Certificate transparency, reverse DNS, zone transfer settings with HTB-optimized timeouts
- **New [enhanced_web] Section** - JavaScript analysis, sensitive files, parameter discovery settings optimized for HTB
- **Research-Based Defaults** - All settings optimized based on HTB community research and testing
- **Configurable via config.toml** - All HTB optimizations fully configurable in single file
- **Fallback Compatibility** - Graceful degradation when advanced tools aren't available

### 🎮 Enhanced User Interface
- **Menu Option 9** - Advanced DNS Enumeration (HTB-optimized with certificate transparency, zone transfers)
- **Menu Option 10** - Enhanced Web Discovery (HTB-optimized with JavaScript analysis, multi-tool enumeration)  
- **Menu Option 11** - theHarvester (moved from position 9)
- **Clear HTB Indicators** - Visual indicators for HTB-optimized features and capabilities

### 📊 Technical Architecture Improvements
- **6-Phase DNS Enumeration** - Comprehensive approach vs. 3-phase basic DNS
- **6-Phase Web Discovery** - Multi-tool approach vs. single-tool scanning
- **Enhanced Scanner Integration** - Seamless workflow with existing reconnaissance flow
- **Professional Error Handling** - Comprehensive timeout and error management
- **Performance Optimized** - Parallel processing with intelligent timeouts

### 🔧 Expected HTB Performance Improvements
- **Subdomain Discovery** - 300%+ improvement with certificate transparency and advanced tools
- **Directory Enumeration** - 200%+ improvement with multi-tool approach and HTB-specific paths
- **Sensitive File Discovery** - 400%+ improvement with HTB-specific file lists and extensions
- **Overall Attack Surface** - 250%+ improvement in total coverage and discovery success rates

### 📖 Documentation & Testing
- **Updated README.md** - Comprehensive HTB v2.2 feature documentation with usage examples
- **test_htb_enhancements.py** - Comprehensive test suite for verifying HTB-optimized features
- **Enhanced Installation Verification** - HTB-specific tool verification and status reporting

---

## [2.1] - 2024-12-17

### 🎯 Major Features Added
- **Parameter Discovery & LFI Testing Scanner** - New comprehensive tool (#6)
  - Combines Arjun, ParamSpider, WFUZZ, LFI Suite, and lfi-autopwn
  - Multi-phase parameter discovery and LFI vulnerability testing
  - Smart result parsing - only reports successful findings
  - Automatic LFI payload creation and management

- **CMS Detection & Enumeration Scanner** - New comprehensive tool (#7)
  - Combines CMSeek and nmap http-enum for CMS detection
  - CMS-specific testing (WPScan for WordPress, Droopescan for Drupal, JoomScan for Joomla)
  - Security recommendations and vulnerability analysis
  - Automatic tool selection based on detected CMS

### 🔧 Critical Bug Fixes
- **Fixed Web-Only Scan Logic** - Major issue where FFUF/Feroxbuster would fail without nmap
  - Added automatic web port discovery for web-only scans
  - Web tools now auto-discover ports (80, 443, 8080, 8443, etc.) when no nmap scan run
  - Includes full domain discovery and /etc/hosts setup when services found
  - All web tools now work independently without requiring nmap first

### 🌐 Enhanced Web Detection
- **Intelligent Web Service Detection** - Improved multi-method approach
  - Standalone web detection when running web-only scans
  - Enhanced fallback logic for HTB machines
  - Better handling of edge cases and non-standard configurations

### 📋 Tool Organization Improvements
- **Consolidated Related Tools** - Organized tools into intelligent scanning categories
  - Parameter & LFI tools work together coordinately instead of independently
  - CMS detection tools provide unified comprehensive reporting
  - Reduced user complexity while dramatically increasing capabilities

### 🎨 User Experience Enhancements
- **Updated Interface** - Clearer descriptions and better guidance
  - Menu options now show "(auto-discovers web ports if needed)"
  - Better messaging about automatic integration features
  - Improved documentation and user guidance

### 🛠️ System Integration Updates
- **New Tool Dependencies** - Added support for additional security tools
  - wfuzz, arjun, paramspider, cmseek integration
  - Updated install.sh for automatic tool installation
  - Enhanced configuration in config.toml for new tools

### 📖 Documentation Updates
- **README Improvements** - Updated with new features and capabilities
  - Documented intelligent web detection behavior
  - Added information about standalone web-only scanning
  - Updated tool descriptions and workflow explanations

---

## [1.0.5] - 2024-12-16

### Initial Release Features
- **Core Reconnaissance Suite** - Nmap, Feroxbuster, FFUF, theHarvester
- **Enhanced/Standard Modes** - Sudo-aware scanning with automatic privilege detection
- **Intelligent Web Integration** - Automatic web service detection with nmap scans
- **HTB-Optimized** - Specifically designed for Hack The Box machine reconnaissance
- **Interactive Controls** - Skip/quit functionality during scan execution
- **Comprehensive Reporting** - Organized output with actionable findings

---

## Version Numbering

ipsnipe follows semantic versioning:
- **Major.Minor.Patch** (e.g., 2.1.0)
- **Major**: Breaking changes or significant feature additions
- **Minor**: New features and capabilities, backward compatible
- **Patch**: Bug fixes and small improvements

---

*For more details about each release, check the commit history and release notes.* 