# ipsnipe ⚡

**Advanced Machine Reconnaissance Framework**

A user-friendly CLI tool for automated penetration testing and reconnaissance. Integrates multiple security tools with intelligent scanning and beautiful output formatting.

```
 ___  ________  ________  ________   ___  ________  _______      
|\  \|\   __  \|\   ____\|\   ___  \|\  \|\   __  \|\  ___ \     
\ \  \ \  \|\  \ \  \___|\ \  \\ \  \ \  \ \  \|\  \ \   __/|    
 \ \  \ \   ____\ \_____  \ \  \\ \  \ \  \ \   ____\ \  \_|/__  
  \ \  \ \  \___|\|____|\  \ \  \\ \  \ \  \ \  \___|\ \  \_|\ \ 
   \ \__\ \__\     ____\_\  \ \__\\ \__\ \__\ \__\    \ \_______\
    \|__|\|__|    |\_________\|__| \|__|\|__|\|__|     \|_______|
                  \|_________|                                   

    ⚡ Advanced Machine Reconnaissance Framework ⚡
    ═══════════════════════════════════════════════
```

## ✨ Features

### 🎯 **Automated Reconnaissance**
- **Multi-tool Integration** - Seamlessly runs Nmap, Gobuster, Feroxbuster, ffuf, Nikto, WhatWeb, theHarvester, and DNSrecon
- **One-Command Execution** - Select individual tools or run comprehensive scans with a single command
- **Sequential Processing** - Intelligently orders scans for optimal results (port discovery → service enumeration → web testing)
- **Progress Tracking** - Real-time status updates with execution times and success/failure indicators

### 🌐 **Smart Web Service Detection**
- **Automatic Port Discovery** - Parses Nmap output to identify open ports and services
- **Web Service Recognition** - Detects HTTP/HTTPS services on any port (not just 80/443)
- **Responsive Port Testing** - Tests web ports for actual content and prioritizes active services
- **Intelligent Skipping** - Automatically skips web-based scans when no web services are detected
- **Protocol Detection** - Determines HTTP vs HTTPS and uses appropriate scanning parameters

### 🔐 **Enhanced/Standard Scanning Modes**
- **Privilege Detection** - Automatically detects sudo access and recommends appropriate mode
- **Enhanced Mode (sudo)**: SYN scans (faster/stealthier), UDP scanning, OS detection, advanced Nmap scripts
- **Standard Mode (no-sudo)**: TCP connect scans, service detection, all web enumeration tools
- **Smart Fallback** - Gracefully handles permission issues and adapts scan techniques
- **Mode Selection** - Force modes via CLI flags (`--enhanced` or `--standard`)

### 🔌 **Flexible Port Configuration**
- **Multiple Formats** - Single ports (`80`), ranges (`1-1000`), lists (`80,443,8080`)
- **Smart Defaults** - HTB-optimized port ranges for quick reconnaissance
- **Custom Targeting** - User-defined port ranges for specific scenarios
- **All-Port Scanning** - Full 65535 port enumeration when needed
- **Service-Specific** - Different port handling for TCP vs UDP scans

### 📊 **Enhanced Output & Reporting**
- **Emoji Highlighting** - Visual indicators for findings (🔓 open ports, 📁 directories, ⚠️ vulnerabilities)
- **Organized Structure** - Timestamped directories with logical file naming
- **Comprehensive Reports** - Detailed SUMMARY_REPORT.md with analysis guidance
- **Execution Metrics** - Timing, file sizes, success rates, and performance data
- **HTB-Specific Tips** - Tailored advice for Hack The Box machine enumeration
- **Finding Categories** - Automatically categorizes and prioritizes discovered information

### ⏸️ **Interactive Scan Control**
- **Skip Individual Scans** - Press 's' + Enter to skip current scan without losing progress
- **Quit All Scans** - Press 'q' + Enter to terminate remaining scans gracefully
- **Progress Tracking** - Real-time scan progress with x/y scan completion counter
- **Graceful Termination** - Proper cleanup of running processes when interrupted
- **Resume-Friendly** - Completed scans are saved even if session is interrupted early

### ⚙️ **Advanced Configuration**
- **TOML Configuration** - Centralized settings in `config.toml` with intelligent defaults
- **Tool Customization** - Adjust timeouts, threads, wordlists, and scan parameters
- **Wordlist Management** - HTB-optimized wordlists with automatic fallbacks
- **Output Control** - Configurable formatting, line length limits, and content highlighting
- **Timeout Management** - Configurable scan timeouts with tool-specific limits

### 🧠 **Intelligent Scanning Logic**
- **Dependency Detection** - Checks for required tools and provides installation guidance
- **Error Handling** - Graceful failure recovery with detailed error reporting
- **Resource Management** - Prevents resource exhaustion with configurable limits
- **Scan Optimization** - Skips redundant scans and focuses on promising targets
- **Adaptive Behavior** - Adjusts scanning approach based on discovered services

### 🛡️ **Security & Ethics**
- **Built-in Disclaimer** - Comprehensive ethical use agreement before scanning
- **Legal Compliance** - Clear guidelines for authorized testing only
- **Attribution Requirements** - Proper crediting for tool usage and modifications
- **Responsible Disclosure** - Guidance on handling discovered vulnerabilities
- **Best Practices** - Educational content on ethical penetration testing

### 🎮 **User Experience**
- **Interactive Interface** - Intuitive menu system with clear options
- **Colorized Output** - Terminal colors for better readability and status indication
- **Demo Mode** - Test interface without running actual scans
- **Verbose Logging** - Detailed debug information when needed
- **Cross-Platform** - Supports Linux, macOS, and Windows (via WSL2)
- **HTB Optimization** - Specifically designed for Hack The Box machine reconnaissance

## 🛠️ Supported Tools

| Tool | Purpose | Enhanced Mode |
|------|---------|---------------|
| **Nmap** | Port/Service scanning | SYN scans, OS detection, UDP |
| **Gobuster/Feroxbuster/ffuf** | Directory enumeration | - |
| **Nikto** | Web vulnerability scanning | - |
| **WhatWeb** | Technology detection | - |
| **theHarvester** | Information gathering | - |
| **DNSrecon** | DNS enumeration | - |

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone https://github.com/hckerhub/ipsnipe.git
cd ipsnipe
chmod +x install.sh && ./install.sh

# 2. Run ipsnipe
python3 ipsnipe.py

# 3. Optional: Force enhanced/standard mode
python3 ipsnipe.py --enhanced   # Force sudo mode
python3 ipsnipe.py --standard   # Force no-sudo mode
```

## 📋 Requirements

- **Python 3.8+**
- **Linux/macOS** (Windows via WSL2)
- **Internet connection** for tool installation

**Supported Systems:**
- ✅ Kali Linux (recommended)
- ✅ Ubuntu/Debian  
- ✅ macOS (via Homebrew)
- ✅ Arch Linux
- ⚠️ Windows (WSL2 only)

## 📖 Usage

### Interactive Mode
```bash
python3 ipsnipe.py
```

1. **Enter target IP** (e.g., `10.10.10.123`)
2. **Choose scan mode** (Enhanced with sudo or Standard)
3. **Select tools** (individual or all)
4. **Configure ports** for Nmap (single, range, or comma-separated)
5. **Start reconnaissance**

### Port Range Examples
```bash
80                    # Single port
1-1000               # Port range  
80,443,8080          # Specific ports
1-65535              # All ports
default              # Use config defaults
```

### Interactive Scan Control
During scan execution, you can control the process:

```bash
# While scans are running:
s + Enter             # Skip current scan, continue with next
q + Enter             # Quit all remaining scans gracefully
Ctrl+C                # Emergency termination (immediate stop)
```

**Benefits:**
- **No Progress Loss** - Completed scans are preserved even if you skip later ones
- **Time Saving** - Skip slow scans if you find what you need
- **Flexible Workflow** - Adapt scanning strategy based on initial results

### Enhanced vs Standard Mode

| Feature | Enhanced (sudo) | Standard |
|---------|----------------|----------|
| TCP Scans | SYN (stealth) | Connect |
| UDP Scans | ✅ Available | ❌ Skipped |
| OS Detection | ✅ Available | ❌ Disabled |
| Speed | Faster | Slower |
| Privileges | Requires sudo | User-level |

## 📁 Output

Creates organized directories with detailed reports:

```
ipsnipe_10.10.10.123_20241201_143022/
├── SUMMARY_REPORT.md      # Overview with analysis tips
├── nmap_quick.txt         # Port scan results
├── gobuster_common.txt    # Directory enumeration
├── nikto.txt             # Web vulnerabilities
└── whatweb.txt           # Technology stack
```

## ⚙️ Configuration

Edit `config.toml` to customize:
- Scan timeouts (default: 5 minutes)
- Wordlist paths
- Tool-specific settings
- Output formatting

## 🐛 Troubleshooting

### Common Issues
```bash
# Tools not found
./install.sh

# Permission errors  
sudo python3 ipsnipe.py

# Python version issues
python3 --version  # Requires 3.8+

# WSL2 networking
sudo service networking restart
```

### Tool Installation
```bash
# Ubuntu/Debian
sudo apt install nmap gobuster nikto dnsrecon ffuf ruby
sudo gem install whatweb

# macOS
brew install nmap gobuster nikto feroxbuster ffuf ruby
gem install whatweb
```

## ⚖️ Legal & Ethical Use

**⚠️ AUTHORIZED USE ONLY**

This tool is for:
- ✅ Authorized penetration testing
- ✅ Your own systems/lab environments  
- ✅ CTF competitions and educational use
- ✅ Bug bounty programs (within scope)

**NOT for:**
- ❌ Unauthorized scanning
- ❌ Systems you don't own/have permission to test
- ❌ Any illegal activities

By using ipsnipe, you agree to use it legally and ethically. The author is not responsible for misuse.

## 👨‍💻 Author & Support

**Created by hckerhub**

- 🌐 **Website:** [hackerhub.me](https://hackerhub.me)
- 🐦 **X:** [@hckerhub](https://x.com/hckerhub)  
- 💻 **GitHub:** [github.com/hckerhub](https://github.com/hckerhub)
- ☕ **Support:** [buymeacoffee.com/hckerhub](https://buymeacoffee.com/hckerhub)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Happy ethical hacking! 🎯** 