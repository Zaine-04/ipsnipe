#!/bin/bash

# ipsnipe Installation Script
# Supports Ubuntu/Debian, macOS, and Kali Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ipsnipe Banner
echo -e "${BLUE}"
cat << "EOF"
 ___  ________  ________  ________   ___  ________  _______      
|\  \|\   __  \|\   ____\|\   ___  \|\  \|\   __  \|\  ___ \     
\ \  \ \  \|\  \ \  \___|\ \  \\ \  \ \  \ \  \|\  \ \   __/|    
 \ \  \ \   ____\ \_____  \ \  \\ \  \ \  \ \   ____\ \  \_|/__  
  \ \  \ \  \___|\|____|\  \ \  \\ \  \ \  \ \  \___|\ \  \_|\ \ 
   \ \__\ \__\     ____\_\  \ \__\\ \__\ \__\ \__\    \ \_______\
    \|__|\|__|    |\_________\|__| \|__|\|__|\|__|     \|_______|
                  \|_________|                                   

    ⚡ Advanced Machine Reconnaissance Framework ⚡
    ════════════════════════════════════════════════
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 ipsnipe Installation Script${NC}"
echo -e "${YELLOW}This script will check dependencies and install missing tools${NC}\n"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt &> /dev/null; then
        OS="debian"
        echo -e "${BLUE}📋 Detected: Debian/Ubuntu-based system${NC}"
    elif command -v pacman &> /dev/null; then
        OS="arch"
        echo -e "${BLUE}📋 Detected: Arch-based system${NC}"
    else
        OS="linux"
        echo -e "${BLUE}📋 Detected: Generic Linux system${NC}"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${BLUE}📋 Detected: macOS${NC}"
else
    echo -e "${RED}❌ Unsupported operating system: $OSTYPE${NC}"
    exit 1
fi

# Check Python version
echo -e "\n${YELLOW}🔍 Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python 3 found: $PYTHON_VERSION${NC}"
    
    # Check if version is 3.8+
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        echo -e "${GREEN}✅ Python version is compatible${NC}"
    else
        echo -e "${RED}❌ Python 3.8+ required. Current version: $PYTHON_VERSION${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Function to check if a tool is installed
check_tool() {
    local tool_name="$1"
    local command_name="${2:-$1}"
    
    if command -v "$command_name" &> /dev/null; then
        echo -e "${GREEN}✅ $tool_name found${NC}"
        return 0
    else
        echo -e "${RED}❌ $tool_name not found${NC}"
        return 1
    fi
}

# Check dependencies
echo -e "\n${YELLOW}🔍 Checking tool dependencies...${NC}"

# Core tools (required)
CORE_TOOLS=(
    "nmap:nmap"
    "gobuster:gobuster" 
    "nikto:nikto"
    "dnsrecon:dnsrecon"
    "curl:curl"
)

# Advanced tools (optional but recommended)
OPTIONAL_TOOLS=(
    "feroxbuster:feroxbuster"
    "ffuf:ffuf"
    "theHarvester:theHarvester"
    "whatweb:whatweb"
    "ruby:ruby"
)

MISSING_CORE=()
MISSING_OPTIONAL=()

echo -e "\n${CYAN}🔍 Core Tools Status:${NC}"
for tool_pair in "${CORE_TOOLS[@]}"; do
    tool_name=$(echo "$tool_pair" | cut -d':' -f1)
    command_name=$(echo "$tool_pair" | cut -d':' -f2)
    
    if ! check_tool "$tool_name" "$command_name"; then
        MISSING_CORE+=("$tool_pair")
    fi
done

echo -e "\n${CYAN}🔍 Optional Tools Status:${NC}"
for tool_pair in "${OPTIONAL_TOOLS[@]}"; do
    tool_name=$(echo "$tool_pair" | cut -d':' -f1)
    command_name=$(echo "$tool_pair" | cut -d':' -f2)
    
    if ! check_tool "$tool_name" "$command_name"; then
        MISSING_OPTIONAL+=("$tool_pair")
    fi
done

# Check Python dependencies
echo -e "\n${CYAN}🔍 Python Dependencies Status:${NC}"
PYTHON_DEPS_MISSING=false
if ! python3 -c "import toml" &> /dev/null; then
    echo -e "${RED}❌ Python package 'toml' not found${NC}"
    PYTHON_DEPS_MISSING=true
else
    echo -e "${GREEN}✅ Python package 'toml' found${NC}"
fi

if ! python3 -c "import colorama" &> /dev/null; then
    echo -e "${RED}❌ Python package 'colorama' not found${NC}"
    PYTHON_DEPS_MISSING=true
else
    echo -e "${GREEN}✅ Python package 'colorama' found${NC}"
fi

if ! python3 -c "import rich" &> /dev/null; then
    echo -e "${RED}❌ Python package 'rich' not found${NC}"
    PYTHON_DEPS_MISSING=true
else
    echo -e "${GREEN}✅ Python package 'rich' found${NC}"
fi

# Summary
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 Installation Summary:${NC}"

if [[ ${#MISSING_CORE[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ All core tools are already installed${NC}"
else
    echo -e "${RED}❌ Missing core tools: ${#MISSING_CORE[@]}${NC}"
    for tool_pair in "${MISSING_CORE[@]}"; do
        tool_name=$(echo "$tool_pair" | cut -d':' -f1)
        echo -e "   • $tool_name"
    done
fi

if [[ ${#MISSING_OPTIONAL[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ All optional tools are already installed${NC}"
else
    echo -e "${YELLOW}⚠️  Missing optional tools: ${#MISSING_OPTIONAL[@]}${NC}"
    for tool_pair in "${MISSING_OPTIONAL[@]}"; do
        tool_name=$(echo "$tool_pair" | cut -d':' -f1)
        echo -e "   • $tool_name"
    done
fi

if [[ "$PYTHON_DEPS_MISSING" == true ]]; then
    echo -e "${RED}❌ Missing Python dependencies${NC}"
else
    echo -e "${GREEN}✅ All Python dependencies are installed${NC}"
fi

# Check if anything needs to be installed
NEEDS_INSTALLATION=false
if [[ ${#MISSING_CORE[@]} -gt 0 || ${#MISSING_OPTIONAL[@]} -gt 0 || "$PYTHON_DEPS_MISSING" == true ]]; then
    NEEDS_INSTALLATION=true
fi

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [[ "$NEEDS_INSTALLATION" == false ]]; then
    echo -e "${GREEN}🎉 All dependencies are already satisfied!${NC}"
    echo -e "${BLUE}💡 ipsnipe is ready to use. Run: ${YELLOW}python3 ipsnipe.py${NC}"
    exit 0
fi

# Ask user if they want to proceed with installation
echo -e "\n${YELLOW}⚠️  Some tools need to be installed for full functionality.${NC}"
echo -e "${BLUE}📋 What will be installed:${NC}"

if [[ ${#MISSING_CORE[@]} -gt 0 ]]; then
    echo -e "${CYAN}🔧 Core tools:${NC}"
    for tool_pair in "${MISSING_CORE[@]}"; do
        tool_name=$(echo "$tool_pair" | cut -d':' -f1)
        echo -e "   • $tool_name"
    done
fi

if [[ ${#MISSING_OPTIONAL[@]} -gt 0 ]]; then
    echo -e "${CYAN}🔧 Optional tools:${NC}"
    for tool_pair in "${MISSING_OPTIONAL[@]}"; do
        tool_name=$(echo "$tool_pair" | cut -d':' -f1)
        echo -e "   • $tool_name"
    done
fi

if [[ "$PYTHON_DEPS_MISSING" == true ]]; then
    echo -e "${CYAN}🐍 Python packages:${NC}"
    echo -e "   • toml, colorama, rich"
fi

echo -e "\n${YELLOW}❓ Do you want to proceed with the installation? (y/N): ${NC}"
read -r RESPONSE

if [[ ! "$RESPONSE" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}💡 Installation cancelled. You can run this script again anytime.${NC}"
    echo -e "${YELLOW}📋 ipsnipe will work with available tools, but some features may be limited.${NC}"
    exit 0
fi

echo -e "\n${GREEN}🚀 Starting installation...${NC}"

# Install Python dependencies first
if [[ "$PYTHON_DEPS_MISSING" == true ]]; then
    echo -e "\n${YELLOW}🐍 Installing Python dependencies...${NC}"
    if [[ -f "requirements.txt" ]]; then
        # Try different methods for installing Python packages
        if pip3 install --user -r requirements.txt &> /dev/null; then
            echo -e "${GREEN}✅ Python dependencies installed (user mode)${NC}"
        elif pip3 install --break-system-packages -r requirements.txt &> /dev/null; then
            echo -e "${GREEN}✅ Python dependencies installed (system packages)${NC}"
        else
            echo -e "${YELLOW}⚠️  Installing essential Python packages individually...${NC}"
            pip3 install --break-system-packages toml colorama rich || {
                echo -e "${RED}❌ Failed to install Python dependencies${NC}"
                echo -e "${YELLOW}💡 You may need to install them manually: pip3 install toml colorama rich${NC}"
            }
        fi
    else
        echo -e "${YELLOW}⚠️  requirements.txt not found, installing essential dependencies${NC}"
        pip3 install --break-system-packages toml colorama rich || {
            echo -e "${RED}❌ Failed to install Python dependencies${NC}"
        }
    fi
fi

# Install system tools based on OS
case $OS in
    "debian")
        echo -e "\n${BLUE}🔄 Updating package list...${NC}"
        sudo apt update
        
        echo -e "${BLUE}🔄 Installing available tools via apt...${NC}"
        # Install what's available via apt
        sudo apt install -y nmap gobuster nikto curl wget ruby ruby-dev
        ;;
        
    "macos")
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ Homebrew not found. Please install Homebrew first:${NC}"
            echo -e "${BLUE}   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            exit 1
        fi
        
        echo -e "\n${BLUE}🔄 Installing tools via Homebrew...${NC}"
        brew install nmap gobuster nikto feroxbuster ffuf ruby
        
        # Set up Ruby path for gems
        echo -e "${BLUE}🔄 Setting up Ruby path...${NC}"
        export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
        ;;
        
    "arch")
        echo -e "\n${BLUE}🔄 Installing tools via pacman...${NC}"
        sudo pacman -S --noconfirm nmap gobuster nikto ruby feroxbuster ffuf
        ;;
esac

# Install tools that need manual installation
echo -e "\n${YELLOW}🔧 Installing tools that require manual setup...${NC}"

# Install DNSrecon from GitHub
if ! command -v dnsrecon &> /dev/null; then
    echo -e "${BLUE}🔄 Installing DNSrecon from GitHub...${NC}"
    if [[ -d "/tmp/dnsrecon" ]]; then
        rm -rf /tmp/dnsrecon
    fi
    
    git clone https://github.com/darkoperator/dnsrecon.git /tmp/dnsrecon
    cd /tmp/dnsrecon
    pip3 install --break-system-packages -r requirements.txt
    sudo cp dnsrecon.py /usr/local/bin/dnsrecon
    sudo chmod +x /usr/local/bin/dnsrecon
    cd - > /dev/null
    echo -e "${GREEN}✅ DNSrecon installed${NC}"
fi

# Install theHarvester from GitHub
if ! command -v theHarvester &> /dev/null; then
    echo -e "${BLUE}🔄 Installing theHarvester from GitHub...${NC}"
    if [[ -d "/tmp/theHarvester" ]]; then
        rm -rf /tmp/theHarvester
    fi
    
    git clone https://github.com/laramies/theHarvester.git /tmp/theHarvester
    cd /tmp/theHarvester
    pip3 install --break-system-packages -r requirements.txt 2>/dev/null || true
    sudo ln -sf "$(pwd)/theHarvester.py" /usr/local/bin/theHarvester
    sudo chmod +x /usr/local/bin/theHarvester
    cd - > /dev/null
    echo -e "${GREEN}✅ theHarvester installed${NC}"
fi

# Install WhatWeb (try multiple methods)
if ! command -v whatweb &> /dev/null; then
    echo -e "${BLUE}🔄 Installing WhatWeb...${NC}"
    
    case $OS in
        "debian")
            # Try apt first, then manual installation
            if sudo apt install -y whatweb 2>/dev/null; then
                echo -e "${GREEN}✅ WhatWeb installed via apt${NC}"
            else
                echo -e "${BLUE}🔄 Installing WhatWeb from GitHub...${NC}"
                if [[ -d "/tmp/WhatWeb" ]]; then
                    rm -rf /tmp/WhatWeb
                fi
                git clone https://github.com/urbanadventurer/WhatWeb.git /tmp/WhatWeb
                sudo cp /tmp/WhatWeb/whatweb /usr/local/bin/
                sudo chmod +x /usr/local/bin/whatweb
                echo -e "${GREEN}✅ WhatWeb installed from GitHub${NC}"
            fi
            ;;
        "macos")
            # Try manual installation for macOS
            echo -e "${BLUE}🔄 Installing WhatWeb from GitHub...${NC}"
            if [[ -d "/tmp/WhatWeb" ]]; then
                rm -rf /tmp/WhatWeb
            fi
            git clone https://github.com/urbanadventurer/WhatWeb.git /tmp/WhatWeb
            sudo cp /tmp/WhatWeb/whatweb /usr/local/bin/
            sudo chmod +x /usr/local/bin/whatweb
            echo -e "${GREEN}✅ WhatWeb installed from GitHub${NC}"
            ;;
        "arch")
            if sudo pacman -S --noconfirm whatweb 2>/dev/null; then
                echo -e "${GREEN}✅ WhatWeb installed via pacman${NC}"
            else
                echo -e "${YELLOW}⚠️  WhatWeb not available via pacman${NC}"
            fi
            ;;
    esac
fi

# Make ipsnipe executable
echo -e "\n${YELLOW}🔧 Setting up ipsnipe...${NC}"
if [[ -f "ipsnipe.py" ]]; then
    chmod +x ipsnipe.py
    echo -e "${GREEN}✅ Made ipsnipe.py executable${NC}"
else
    echo -e "${RED}❌ ipsnipe.py not found in current directory${NC}"
    echo -e "${YELLOW}💡 Make sure you're running this script from the ipsnipe directory${NC}"
fi

# Set up wordlists
echo -e "\n${YELLOW}📁 Setting up wordlists...${NC}"

# Create wordlist directories
WORDLIST_DIRS=("/usr/share/wordlists" "/usr/share/wordlists/dirb" "/usr/share/wordlists/dirbuster" "/usr/share/seclists")

for dir in "${WORDLIST_DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        echo -e "${BLUE}🔄 Creating wordlist directory: $dir${NC}"
        sudo mkdir -p "$dir"
    fi
done

# Set up basic wordlists if SecLists isn't available
if [[ ! -d "/usr/share/seclists" ]]; then
    echo -e "${BLUE}🔄 Setting up basic wordlists...${NC}"
    
    # Create a basic common.txt for dirb
    if [[ ! -f "/usr/share/wordlists/dirb/common.txt" ]]; then
        echo -e "${BLUE}🔄 Creating basic dirb wordlist...${NC}"
        sudo tee "/usr/share/wordlists/dirb/common.txt" > /dev/null << 'EOF'
admin
administrator
login
dashboard
panel
config
backup
uploads
files
images
css
js
api
test
dev
development
staging
tmp
temp
robots.txt
.htaccess
sitemap.xml
EOF
    fi
    
    # Create a basic directory-list for dirbuster
    if [[ ! -f "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt" ]]; then
        echo -e "${BLUE}🔄 Creating basic dirbuster wordlist...${NC}"
        sudo cp "/usr/share/wordlists/dirb/common.txt" "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
    fi
fi

# Final verification
echo -e "\n${YELLOW}🔍 Verifying installation...${NC}"

VERIFICATION_FAILED=false

echo -e "\n${CYAN}🔍 Verification Results:${NC}"
for tool_pair in "${CORE_TOOLS[@]}"; do
    tool_name=$(echo "$tool_pair" | cut -d':' -f1)
    command_name=$(echo "$tool_pair" | cut -d':' -f2)
    
    if ! check_tool "$tool_name" "$command_name"; then
        VERIFICATION_FAILED=true
    fi
done

for tool_pair in "${OPTIONAL_TOOLS[@]}"; do
    tool_name=$(echo "$tool_pair" | cut -d':' -f1)
    command_name=$(echo "$tool_pair" | cut -d':' -f2)
    
    check_tool "$tool_name" "$command_name" || true  # Don't fail on optional tools
done

# Test ipsnipe
echo -e "\n${YELLOW}🧪 Testing ipsnipe...${NC}"
if python3 ipsnipe.py --version &> /dev/null; then
    echo -e "${GREEN}✅ ipsnipe is working correctly${NC}"
else
    echo -e "${YELLOW}⚠️  ipsnipe test inconclusive (might still work)${NC}"
fi

# Final message
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Installation completed!${NC}"

if [[ "$VERIFICATION_FAILED" == false ]]; then
    echo -e "${GREEN}✅ All core tools are installed and ready to use${NC}"
    echo -e "\n${BLUE}🚀 To start ipsnipe, run:${NC}"
    echo -e "${YELLOW}   python3 ipsnipe.py${NC}"
else
    echo -e "${YELLOW}⚠️  Some core tools may not be available. Check the verification results above.${NC}"
    echo -e "${BLUE}💡 ipsnipe will work with available tools, but some features may be limited.${NC}"
    echo -e "\n${BLUE}🚀 You can still try running ipsnipe:${NC}"
    echo -e "${YELLOW}   python3 ipsnipe.py${NC}"
fi

echo -e "\n${CYAN}📋 Important Notes:${NC}"
echo -e "${BLUE}• ipsnipe includes an ethical use disclaimer${NC}"
echo -e "${BLUE}• You must agree to use the tool legally and ethically${NC}"
echo -e "${BLUE}• Some tools may require additional configuration for full functionality${NC}"

echo -e "\n${BLUE}📖 For more information, check:${NC}"
echo -e "${YELLOW}• README.md - Complete documentation${NC}"
echo -e "${YELLOW}• QUICKSTART.md - Quick start guide${NC}"
echo -e "${YELLOW}• config.toml - Configuration options${NC}"

echo -e "\n${GREEN}Happy ethical hacking! 🎯${NC}"
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ipsnipe created by hckerhub${NC}"
echo -e "${BLUE}🌐 Website: ${CYAN}https://hackerhub.me${NC}"
echo -e "${BLUE}🐦 X: ${CYAN}@hckerhub${NC}"
echo -e "${BLUE}☕ Support: ${CYAN}https://buymeacoffee.com/hckerhub${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" 