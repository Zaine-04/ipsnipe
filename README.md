# BoxRecon ⚡

**Advanced Machine Reconnaissance Framework**

A user-friendly command-line interface tool designed to facilitate reconnaissance on any target machine. BoxRecon automates common penetration testing tools and presents results in an easy-to-read format.

```
██████╗  ██████╗ ██╗  ██╗██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗╚██╗██╔╝██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
██████╔╝██║   ██║ ╚███╔╝ ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██╗██║   ██║ ██╔██╗ ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██╔╝ ██╗██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

    ⚡ Advanced Machine Reconnaissance Framework ⚡
    ═══════════════════════════════════════════════
```

## ✨ Features

- **🎨 Beautiful ASCII Art Interface** - Eye-catching terminal UI with colors
- **🔍 Automated Reconnaissance** - Run multiple tools with a single command
- **📊 Enhanced Output Formatting** - Results with emoji highlights and better readability
- **📋 Comprehensive Summary Reports** - Detailed Markdown reports with HTB-specific guidance
- **⚙️ TOML Configuration** - Customizable settings via config.toml file
- **⏰ Configurable Timeouts** - 5-minute default timeout with user customization
- **🎯 HTB-Optimized Wordlists** - Smaller, focused wordlists perfect for HTB machines
- **🛡️ Input Validation** - IP address validation and error handling
- **⚡ Flexible Scanning** - Choose individual tools or run all at once
- **🕐 Progress Tracking** - Real-time status updates and execution times
- **🎭 Demo Mode** - Test the interface without running actual scans
- **⚖️ Ethical Use Disclaimer** - Built-in legal and ethical use agreement

## 🛠️ Supported Tools

| Tool | Purpose | Description |
|------|---------|-------------|
| **Nmap** | Port Scanning | TCP/UDP port scans with service detection |
| **Gobuster** | Directory Enumeration | Web directory and file discovery |
| **Feroxbuster** | Fast Directory Enumeration | Rust-based high-performance directory brute-forcer |
| **ffuf** | Web Fuzzing | Fast web fuzzer for directories, files, and parameters |
| **Nikto** | Web Vulnerability Scanner | Comprehensive web application testing |
| **WhatWeb** | Technology Detection | Identify web technologies and frameworks |
| **theHarvester** | Information Gathering | Email addresses and subdomain enumeration |
| **DNSrecon** | DNS Enumeration | DNS record enumeration and zone transfers |

## 📋 Requirements

### **System Requirements**
- **Python 3.8+** (tested with Python 3.12.10)
- **Unix-like OS** (Linux, macOS, or WSL2 on Windows)
- **Terminal with color support**
- **Internet connection** (for tool installation and wordlist downloads)
- **Sudo privileges** (for tool installation and some scans)

### **Supported Operating Systems**

| OS | Version | Status | Notes |
|----|---------|--------|-------|
| **Kali Linux** | 2020.1+ | ✅ Recommended | Most tools pre-installed |
| **Ubuntu** | 18.04+ | ✅ Full Support | Complete auto-installation |
| **Debian** | 10+ | ✅ Full Support | Complete auto-installation |
| **Parrot Security** | 4.0+ | ✅ Full Support | Security-focused distro |
| **Arch Linux** | Current | ✅ Full Support | Uses pacman/AUR |
| **macOS** | 10.15+ | ✅ Full Support | Requires Homebrew |
| **Windows** | 10/11 | ⚠️ WSL2 Only | Use WSL2 with Ubuntu |

### **Required Tools**

The `install.sh` script automatically installs these tools:

#### **Core Network Tools**
- **nmap** - Network scanner and port discovery
- **gobuster** - Directory and file enumeration
- **nikto** - Web vulnerability scanner
- **dnsrecon** - DNS enumeration and zone transfers

#### **Modern Enumeration Tools**
- **feroxbuster** - High-performance directory brute-forcer
- **ffuf** - Fast web fuzzer for directories and parameters
- **theharvester** - Email and subdomain gathering

#### **Technology Detection**
- **whatweb** - Web technology identification (Ruby gem)

#### **Manual Installation (if needed)**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nmap gobuster nikto dnsrecon theharvester ffuf ruby ruby-dev
sudo gem install whatweb

# macOS (with Homebrew)
brew install nmap gobuster nikto dnsrecon feroxbuster ffuf ruby
gem install whatweb

# Arch Linux
sudo pacman -S nmap gobuster nikto ruby dnsrecon feroxbuster ffuf
sudo gem install whatweb
```

### **Python Dependencies**
```bash
pip3 install -r requirements.txt
```

**Included packages:**
- `toml` - Configuration file parsing (with fallback parser)
- `colorama` - Cross-platform colored terminal output

**Note:** BoxRecon includes fallback TOML parsing, so it works even without external dependencies.

### **Wordlists**
BoxRecon uses optimized wordlists for HTB machines:
- **Primary:** `/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt`
- **Fallback:** `/usr/share/wordlists/dirb/common.txt`
- **Auto-generated:** Minimal HTB-focused wordlist if none found

### **Network Requirements**
- **HTB VPN connection** (for scanning HTB machines)
- **Internet access** (for tool installation and updates)
- **Firewall permissions** (for outbound scanning traffic)

## 🚀 Installation

### **Quick Start (Recommended)**

```bash
# 1. Clone the repository
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon

# 2. Run the automated installer
chmod +x install.sh
./install.sh

# 3. Start BoxRecon
python3 boxrecon.py
```

### **Manual Installation**

If you prefer manual installation or the automated script doesn't work:

1. **Clone the repository:**
```bash
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon
```

2. **Install system dependencies:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nmap gobuster nikto dnsrecon theharvester ffuf ruby ruby-dev
sudo gem install whatweb

# macOS (requires Homebrew)
brew install nmap gobuster nikto dnsrecon feroxbuster ffuf ruby
gem install whatweb

# Arch Linux
sudo pacman -S nmap gobuster nikto ruby dnsrecon feroxbuster ffuf
sudo gem install whatweb
```

3. **Install Python dependencies:**
```bash
pip3 install -r requirements.txt
```

4. **Make executable:**
```bash
chmod +x boxrecon.py
```

5. **Verify installation:**
```bash
python3 boxrecon.py --version
```

### **Test Installation**
```bash
# Test the interface without running actual scans
python3 demo.py
```

### **What the install.sh Script Does**

The automated installer performs the following actions:

1. **🔍 System Detection**
   - Detects your operating system (Ubuntu/Debian, macOS, Arch Linux)
   - Checks Python 3.8+ requirement
   - Validates system compatibility

2. **📦 Core Tool Installation**
   - **nmap** - Network scanner for port discovery
   - **gobuster** - Directory/file enumeration
   - **nikto** - Web vulnerability scanner
   - **dnsrecon** - DNS enumeration tool

3. **💎 Ruby-based Tools**
   - Installs Ruby and gem if needed
   - **whatweb** - Web technology identification

4. **🚀 Modern Tools**
   - **feroxbuster** - High-performance directory brute-forcer
   - **ffuf** - Fast web fuzzer
   - **theharvester** - Information gathering tool

5. **📁 Wordlist Setup**
   - Downloads HTB-optimized wordlists
   - Creates directory structure in `/usr/share/wordlists/`
   - Sets up fallback wordlists if downloads fail

6. **🐍 Python Dependencies**
   - Installs required Python packages
   - Sets up TOML configuration parsing

7. **✅ Verification**
   - Tests all installed tools
   - Verifies BoxRecon functionality
   - Reports any missing dependencies

**Installation Log:**
The script provides colored output showing each step and any issues encountered.

## 🖥️ Platform Compatibility

### ✅ **Fully Supported Platforms**

| Platform | Status | Installation Method | Notes |
|----------|--------|-------------------|-------|
| **🐧 Kali Linux** | ✅ Recommended | `./install.sh` | Most tools pre-installed |
| **🐧 Ubuntu/Debian** | ✅ Full Support | `./install.sh` | Complete auto-installation |
| **🐧 Parrot Security** | ✅ Full Support | `./install.sh` | Security-focused distro |
| **🐧 Arch Linux** | ✅ Full Support | `./install.sh` | Uses pacman |
| **🍎 macOS** | ✅ Full Support | `./install.sh` | Requires Homebrew |

### ⚠️ **Limited/Workaround Support**

| Platform | Status | Workaround | Notes |
|----------|--------|------------|-------|
| **🪟 Windows** | ❌ Not Supported | WSL2/VM | See Windows section below |
| **🐧 Other Linux** | ⚠️ Manual Install | Package manager | Manual tool installation |

### **🐧 Linux Distribution Specific**

#### **Kali Linux (Recommended for HTB)**
```bash
# Most tools already available
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon
./install.sh  # Adds any missing tools
python3 boxrecon.py
```

#### **Ubuntu/Debian**
```bash
# Full installation with apt
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon
./install.sh  # Installs all dependencies
python3 boxrecon.py
```

#### **Arch Linux**
```bash
# Uses pacman and AUR
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon
./install.sh  # Uses pacman for installation
python3 boxrecon.py
```

### **🍎 macOS Installation**

**Prerequisites:**
- **Homebrew** (install from [brew.sh](https://brew.sh))
- **Xcode Command Line Tools**

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install BoxRecon
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon
./install.sh  # Uses brew for installation
python3 boxrecon.py
```

### **🪟 Windows Users**

BoxRecon is designed for Unix-like systems and doesn't run natively on Windows. Here are your options:

#### **Option 1: WSL2 (Recommended)**
```bash
# 1. Install WSL2 with Ubuntu
wsl --install -d Ubuntu

# 2. Restart and open Ubuntu terminal
# 3. Install BoxRecon in WSL2
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon
./install.sh
python3 boxrecon.py
```

#### **Option 2: Virtual Machine**
1. Install **VirtualBox** or **VMware**
2. Create VM with **Kali Linux** or **Ubuntu**
3. Follow Linux installation steps
4. Connect to HTB VPN from VM

#### **Option 3: Docker (Advanced)**
```bash
# Run BoxRecon in a Linux container
docker run -it --rm ubuntu:22.04 bash
# Then follow Ubuntu installation steps
```

### **🎯 HTB Machine Usage Context**

**Important:** BoxRecon runs **FROM your attacking machine TO scan HTB targets**, not ON the HTB machines.

```bash
# Typical HTB workflow:
# 1. Connect to HTB VPN on your machine
openvpn lab_username.ovpn

# 2. Run BoxRecon from your attacking machine
python3 boxrecon.py

# 3. Enter HTB machine IP when prompted
🎯 Enter target IP address: 10.10.10.123
```

**Recommended Setup for HTB:**
- **Primary:** Kali Linux (VM or bare metal)
- **Alternative:** Ubuntu with security tools
- **macOS:** Works well with Homebrew
- **Windows:** Use WSL2 with Ubuntu

## 📖 Usage

### Basic Usage
```bash
python3 boxrecon.py
```

### Command Line Options
```bash
python3 boxrecon.py --help            # Show help
python3 boxrecon.py --version         # Show version
python3 boxrecon.py --skip-disclaimer # Skip ethical disclaimer (for automation)
```

**Note:** The `--skip-disclaimer` flag is intended for automated scripts where user interaction isn't possible. You are still legally and ethically bound to use the tool responsibly.

### Interactive Workflow

1. **Start BoxRecon:**
   ```bash
   python3 boxrecon.py
   ```

2. **Enter target IP:**
   ```
   🎯 Enter target IP address: 10.10.10.123
   ```

3. **Select reconnaissance options:**
   ```
   🔍 Available Reconnaissance Options:
   1. Quick Nmap Scan (Top 1000 ports)
   2. Full Nmap Scan (All ports)
   3. Gobuster - Common wordlist
   4. Gobuster - Big wordlist
   5. Nikto Web Scanner
   6. WhatWeb Technology Detection
   7. Run All Attacks
   0. Custom Selection (comma-separated)
   
   🎯 Select attack options (e.g., 1,3,5 or 7 for all): 1,3,5
   ```

4. **Confirm and run:**
   ```
   📋 Selected attacks:
     • Nmap Quick
     • Gobuster Common
     • Nikto
   
   🚀 Start reconnaissance? (y/N): y
   ```

## 📁 Output Structure

BoxRecon creates organized output directories:

```
boxrecon_10.10.10.123_20241201_143022/
├── SUMMARY_REPORT.md      # Overview of all scans
├── nmap_quick.txt         # Nmap quick scan results
├── gobuster_common.txt    # Gobuster directory enumeration
├── nikto.txt             # Nikto web vulnerability scan
└── whatweb.txt           # WhatWeb technology detection
```

### Sample Output Files

**SUMMARY_REPORT.md:**
```markdown
# BoxRecon Reconnaissance Report

**Target IP:** 10.10.10.123
**Scan Date:** 2024-12-01 14:30:22
**Output Directory:** boxrecon_10.10.10.123_20241201_143022

## Executed Scans

- ✅ **Nmap Quick**
  - Status: success
  - Output File: `nmap_quick.txt`
  - Execution Time: 45.23 seconds

## Quick Analysis Tips

1. **Check Nmap results** for open ports and services
2. **Review Gobuster output** for hidden directories and files
3. **Examine Nikto results** for web vulnerabilities
4. **Look at WhatWeb output** for technology stack information
```

## 🎯 Scan Types

### 1. Network Scanning
- **Nmap Quick:** Top 1000 TCP ports with service detection
- **Nmap Full:** All 65535 TCP ports with vulnerability scripts
- **Nmap UDP:** Top 200 UDP ports (requires sudo)

### 2. Web Directory Enumeration
- **Gobuster Common:** Fast directory enumeration with common wordlist
- **Gobuster Big:** Comprehensive enumeration with extended wordlist
- **Feroxbuster:** High-performance Rust-based directory brute-forcer
- **ffuf:** Fast web fuzzer for directories and files

### 3. Web Analysis
- **Nikto:** Web vulnerability assessment
- **WhatWeb:** Technology stack identification

### 4. Information Gathering
- **theHarvester:** Email addresses and subdomain enumeration
- **DNSrecon:** DNS record enumeration and zone transfers

## 🔧 Configuration

BoxRecon uses a `config.toml` file for customization. The configuration is automatically created with sensible defaults.

### Key Configuration Options

**Timeouts:**
```toml
[general]
scan_timeout = 300  # 5 minutes (HTB-optimized)
```

**Wordlists (HTB-optimized):**
```toml
[wordlists]
common = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
small = "/usr/share/wordlists/dirb/common.txt"
big = "/usr/share/wordlists/dirb/big.txt"
```

**Output Formatting:**
```toml
[output]
highlight_important = true  # Emoji highlights for findings
max_line_length = 120
truncate_long_lines = true
```

### Customizing Configuration
Edit `config.toml` to adjust:
- Scan timeouts
- Wordlist paths
- Tool-specific settings
- Output formatting options

## 🐛 Troubleshooting

### **Installation Issues**

#### **1. "Command not found" errors:**
```bash
# Check which tools are missing
which nmap gobuster nikto feroxbuster ffuf theHarvester dnsrecon
gem list | grep whatweb

# Re-run installer to fix missing tools
./install.sh

# Manual installation for specific tools
sudo apt install nmap gobuster nikto  # Ubuntu/Debian
brew install nmap gobuster nikto      # macOS
```

#### **2. Permission denied:**
```bash
# Make scripts executable
chmod +x boxrecon.py install.sh

# For Nmap SYN/UDP scans, use sudo
sudo python3 boxrecon.py

# Fix Python permissions
sudo chown -R $USER:$USER ~/.local/
```

#### **3. Python version issues:**
```bash
# Check Python version (requires 3.8+)
python3 --version

# Install Python 3.8+ if needed
sudo apt install python3.8 python3.8-pip  # Ubuntu
brew install python@3.8                    # macOS
```

#### **4. Homebrew issues (macOS):**
```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update Homebrew
brew update && brew upgrade

# Fix permissions
sudo chown -R $(whoami) /usr/local/var/homebrew
```

### **Runtime Issues**

#### **1. Wordlist not found:**
```bash
# Install wordlists (Kali Linux)
sudo apt install wordlists

# Download manually
sudo mkdir -p /usr/share/wordlists/dirb
sudo wget https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt -O /usr/share/wordlists/dirb/common.txt

# BoxRecon will create minimal wordlist if none found
```

#### **2. Network connectivity issues:**
```bash
# Test target connectivity
ping 10.10.10.123

# Check HTB VPN connection
ip route | grep tun0

# Verify DNS resolution
nslookup 10.10.10.123
```

#### **3. Timeout issues:**
```bash
# Increase timeout in config.toml
[general]
scan_timeout = 600  # 10 minutes instead of 5

# Use smaller wordlists for faster scans
[wordlists]
common = "/usr/share/wordlists/dirb/common.txt"  # smaller list
```

#### **4. Tool-specific errors:**
```bash
# Test individual tools
nmap -sS -T4 --top-ports 100 10.10.10.123
gobuster dir -u http://10.10.10.123 -w /usr/share/wordlists/dirb/common.txt
nikto -h 10.10.10.123

# Check tool versions
nmap --version
gobuster version
```

### **Platform-Specific Issues**

#### **WSL2 (Windows)**
```bash
# Update WSL2
wsl --update

# Fix networking issues
sudo service networking restart

# Install missing packages
sudo apt update && sudo apt upgrade
```

#### **macOS**
```bash
# Fix Ruby gem permissions
gem install --user-install whatweb

# Update Xcode Command Line Tools
xcode-select --install
```

#### **Arch Linux**
```bash
# Update package database
sudo pacman -Sy

# Install from AUR if needed
yay -S feroxbuster-bin ffuf-bin
```

### **Debug Mode**

#### **Verbose Output:**
```bash
# Enable verbose logging in config.toml
[general]
verbose_logging = true

# Check individual tool outputs
ls -la boxrecon_*/
cat boxrecon_*/SUMMARY_REPORT.md
```

#### **Test Mode:**
```bash
# Test interface without actual scans
python3 demo.py

# Check configuration loading
python3 -c "from boxrecon import BoxRecon; h = BoxRecon(); print('Config loaded successfully')"
```

### **Getting Help**

If you're still having issues:

1. **Check the generated output files** in `boxrecon_*` directories
2. **Run with sudo** if getting permission errors
3. **Update your system** and try reinstalling
4. **Check GitHub Issues** for similar problems
5. **Create a new issue** with error details and system info

```bash
# Gather system info for bug reports
uname -a
python3 --version
which nmap gobuster nikto
./install.sh 2>&1 | tee install.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Ethical Use & Legal Disclaimer

### 🔒 **IMPORTANT: Read Before Use**

**BoxRecon is designed EXCLUSIVELY for authorized security testing and educational purposes.**

### ✅ **Authorized Use Cases**
- **Penetration testing** with explicit written authorization
- **Security research** on systems you own
- **Educational purposes** in controlled lab environments
- **Bug bounty programs** within defined scope
- **Capture The Flag (CTF)** competitions
- **Personal learning** on your own infrastructure

### ❌ **Prohibited Activities**
- Scanning systems without explicit permission
- Unauthorized network reconnaissance
- Testing third-party systems without consent
- Any illegal or malicious activities
- Violating terms of service or acceptable use policies

### 📋 **Legal Requirements**
By using BoxRecon, you acknowledge that:
- You have **explicit authorization** to test target systems
- You will **comply with all applicable laws** (local, state, federal, international)
- You understand that **unauthorized access is illegal** in most jurisdictions
- You will use this tool **responsibly and ethically**

### 🚫 **Limitation of Liability**
The author (hckerhub) is **NOT responsible** for:
- Any damages to personal property or systems
- Legal consequences from tool misuse
- Unauthorized access or illegal activities
- Data loss, system compromise, or service disruption
- Any direct, indirect, incidental, or consequential damages

### 🛡️ **Best Practices**
1. **Always obtain written permission** before testing
2. **Document your authorization** and scope
3. **Follow responsible disclosure** for any findings
4. **Respect system resources** and avoid disruption
5. **Stay within defined scope** and time windows
6. **Report findings appropriately** to system owners

### ⚖️ **Legal Notice**
Users are solely responsible for ensuring their use complies with applicable laws and regulations. This tool should only be used in accordance with ethical hacking principles and with proper authorization.

## 👨‍💻 Author

**BoxRecon** is created and maintained by **hckerhub**

- **🐦 X (Twitter):** [@hckerhub](https://x.com/hckerhub)
- **🌐 Website:** [hackerhub.me](https://hackerhub.me)
- **💻 GitHub:** [github.com/hckerhub](https://github.com/hckerhub)
- **☕ Buy Me a Coffee:** [buymeacoffee.com/hckerhub](https://buymeacoffee.com/hckerhub)

## 🙏 Acknowledgments

- Hack The Box for providing an excellent learning platform
- The developers of Nmap, Gobuster, Nikto, and WhatWeb
- The cybersecurity community for continuous tool development

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/hckerhub/BoxRecon/issues)
- **Documentation:** This README and inline code comments
- **Community:** HTB Discord/Forums
- **Support the Project:** [Buy Me a Coffee ☕](https://buymeacoffee.com/hckerhub)

---

**Happy Hacking! 🎯**

*Created with ❤️ by [hckerhub](https://hackerhub.me)* 