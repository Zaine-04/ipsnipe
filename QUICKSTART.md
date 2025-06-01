# BoxRecon Quick Start Guide 🚀

Get up and running with BoxRecon in under 5 minutes!

## 🏃‍♂️ Super Quick Start

```bash
# 1. Clone and enter directory
git clone https://github.com/hckerhub/BoxRecon.git
cd BoxRecon

# 2. Run the installer (handles everything)
chmod +x install.sh
./install.sh

# 3. Start BoxRecon
python3 boxrecon.py
```

## 🎯 Basic Usage

1. **Enter target IP** when prompted (e.g., `10.10.10.123`)
2. **Select scans** you want to run:
   - `1` = Quick Nmap scan (recommended for starters)
   - `3` = Web directory enumeration
   - `7` = Run everything (for comprehensive recon)
3. **Confirm** and let BoxRecon do the work!
4. **Check results** in the generated `boxrecon_*` directory

## 🎭 Try the Demo First

Want to see how it works without installing tools?

```bash
python3 demo.py
```

This shows the full interface without running actual scans.

## 🛠️ Manual Installation (if installer fails)

### macOS
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install nmap gobuster nikto
gem install whatweb
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install nmap gobuster nikto ruby ruby-dev
sudo gem install whatweb
```

### Kali Linux
```bash
# Most tools are pre-installed, just add WhatWeb
sudo gem install whatweb
```

## 📋 Common Scan Combinations

| Use Case | Select Options | Description |
|----------|----------------|-------------|
| **Quick Check** | `1` | Fast TCP port scan only |
| **Web App** | `1,4,8` | TCP ports + directories + web vulns |
| **Full Network** | `1,2,3` | TCP + UDP + all ports |
| **Directory Enum** | `4,6,7` | Multiple directory enumeration tools |
| **Full Recon** | `12` | Everything (takes longer) |
| **Custom** | `1,3,4,6,8,9` | Pick exactly what you need |

## 📁 Understanding Output

After scans complete, check the `boxrecon_*` directory:

- **`SUMMARY_REPORT.md`** - Start here! Overview of all findings
- **`nmap_*.txt`** - Open ports and services
- **`gobuster_*.txt`** - Hidden web directories
- **`nikto.txt`** - Web vulnerabilities
- **`whatweb.txt`** - Technology stack

## 🔧 Troubleshooting

**"Command not found" errors?**
```bash
# Check what's missing
which nmap gobuster nikto
gem list | grep whatweb

# Re-run installer
./install.sh
```

**Permission denied?**
```bash
# For Nmap SYN scans, use sudo
sudo python3 boxrecon.py
```

**Wordlists not found?**
```bash
# Download manually
sudo mkdir -p /usr/share/wordlists/dirb
sudo wget https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt -O /usr/share/wordlists/dirb/common.txt
```

## 🎯 Pro Tips

1. **Start with option 1** (quick Nmap) to get familiar
2. **Use option 7** for comprehensive recon on real HTB machines
3. **Check the summary report first** before diving into individual files
4. **Look for emoji highlights** - 🔓 for open ports, 📁 for directories, ⚠️ for vulnerabilities
5. **Customize timeouts** in `config.toml` if scans take too long (default: 5 minutes)
6. **Run with sudo** if you get permission errors
7. **Keep results organized** - each run creates a timestamped directory

## ⚙️ Configuration Tips

**Adjust scan timeout for HTB machines:**
```bash
# Edit config.toml
[general]
scan_timeout = 180  # 3 minutes for faster machines
```

**Use smaller wordlists for speed:**
```bash
# BoxRecon defaults to small, HTB-optimized wordlists
# Perfect for most HTB machines
```

## 🆘 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Look at the generated output files for debugging
- Ensure all tools are properly installed with `./install.sh`

---

**Ready to hack? Run `python3 boxrecon.py` and let's go! 🎯**

*Created with ❤️ by [hckerhub](https://hackerhub.me) | Support: [Buy Me a Coffee ☕](https://buymeacoffee.com/hckerhub)* 