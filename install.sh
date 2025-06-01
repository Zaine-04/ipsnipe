#!/bin/bash

# BoxRecon Installation Script
# Supports Ubuntu/Debian, macOS, and Kali Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# BoxRecon Banner
echo -e "${BLUE}"
cat << "EOF"
██████╗  ██████╗ ██╗  ██╗██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗╚██╗██╔╝██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
██████╔╝██║   ██║ ╚███╔╝ ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██╗██║   ██║ ██╔██╗ ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝██╔╝ ██╗██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

    ⚡ Advanced Machine Reconnaissance Framework ⚡
    ═══════════════════════════════════════════════
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 BoxRecon Installation Script${NC}"
echo -e "${YELLOW}This script will install BoxRecon and its dependencies${NC}\n"

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

# Install system dependencies
echo -e "\n${YELLOW}📦 Installing system dependencies...${NC}"

case $OS in
    "debian")
        echo -e "${BLUE}🔄 Updating package list...${NC}"
        sudo apt update
        
        echo -e "${BLUE}🔄 Installing tools...${NC}"
        sudo apt install -y nmap gobuster nikto curl wget dnsrecon
        
        # Install Ruby for WhatWeb
        if ! command -v gem &> /dev/null; then
            echo -e "${BLUE}🔄 Installing Ruby...${NC}"
            sudo apt install -y ruby ruby-dev
        fi
        ;;
        
    "macos")
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ Homebrew not found. Please install Homebrew first:${NC}"
            echo -e "${BLUE}   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            exit 1
        fi
        
        echo -e "${BLUE}🔄 Installing tools via Homebrew...${NC}"
        brew install nmap gobuster nikto dnsrecon
        
        # Install Ruby if not present
        if ! command -v gem &> /dev/null; then
            echo -e "${BLUE}🔄 Installing Ruby...${NC}"
            brew install ruby
        fi
        ;;
        
    "arch")
        echo -e "${BLUE}🔄 Installing tools via pacman...${NC}"
        sudo pacman -S --noconfirm nmap gobuster nikto ruby dnsrecon
        ;;
        
    *)
        echo -e "${YELLOW}⚠️  Please install the following tools manually:${NC}"
        echo -e "   - nmap"
        echo -e "   - gobuster"
        echo -e "   - nikto"
        echo -e "   - ruby (for WhatWeb)"
        ;;
esac

# Install WhatWeb
echo -e "\n${YELLOW}🔍 Installing WhatWeb...${NC}"
if command -v gem &> /dev/null; then
    if gem list whatweb | grep -q whatweb; then
        echo -e "${GREEN}✅ WhatWeb already installed${NC}"
    else
        echo -e "${BLUE}🔄 Installing WhatWeb via gem...${NC}"
        if [[ "$OS" == "macos" ]]; then
            gem install whatweb
        else
            sudo gem install whatweb
        fi
    fi
else
    echo -e "${RED}❌ Ruby/gem not available. WhatWeb installation skipped.${NC}"
fi

# Install additional tools
echo -e "\n${YELLOW}🔍 Installing additional reconnaissance tools...${NC}"

# Install feroxbuster
if ! command -v feroxbuster &> /dev/null; then
    echo -e "${BLUE}🔄 Installing feroxbuster...${NC}"
    case $OS in
        "debian")
            # Download and install feroxbuster from GitHub releases
            FEROX_VERSION="2.10.1"
            wget -q "https://github.com/epi052/feroxbuster/releases/download/v${FEROX_VERSION}/feroxbuster_${FEROX_VERSION}_x86_64-linux-musl.tar.gz" -O /tmp/feroxbuster.tar.gz
            sudo tar -xzf /tmp/feroxbuster.tar.gz -C /usr/local/bin/ feroxbuster
            sudo chmod +x /usr/local/bin/feroxbuster
            rm /tmp/feroxbuster.tar.gz
            ;;
        "macos")
            brew install feroxbuster
            ;;
        "arch")
            sudo pacman -S --noconfirm feroxbuster
            ;;
    esac
    echo -e "${GREEN}✅ feroxbuster installed${NC}"
else
    echo -e "${GREEN}✅ feroxbuster already installed${NC}"
fi

# Install ffuf
if ! command -v ffuf &> /dev/null; then
    echo -e "${BLUE}🔄 Installing ffuf...${NC}"
    case $OS in
        "debian")
            sudo apt install -y ffuf 2>/dev/null || {
                # Fallback: install from GitHub releases
                FFUF_VERSION="2.1.0"
                wget -q "https://github.com/ffuf/ffuf/releases/download/v${FFUF_VERSION}/ffuf_${FFUF_VERSION}_linux_amd64.tar.gz" -O /tmp/ffuf.tar.gz
                sudo tar -xzf /tmp/ffuf.tar.gz -C /usr/local/bin/ ffuf
                sudo chmod +x /usr/local/bin/ffuf
                rm /tmp/ffuf.tar.gz
            }
            ;;
        "macos")
            brew install ffuf
            ;;
        "arch")
            sudo pacman -S --noconfirm ffuf
            ;;
    esac
    echo -e "${GREEN}✅ ffuf installed${NC}"
else
    echo -e "${GREEN}✅ ffuf already installed${NC}"
fi

# Install theHarvester
if ! command -v theHarvester &> /dev/null; then
    echo -e "${BLUE}🔄 Installing theHarvester...${NC}"
    case $OS in
        "debian")
            sudo apt install -y theharvester 2>/dev/null || {
                echo -e "${YELLOW}⚠️  theHarvester not available in repos, install manually if needed${NC}"
            }
            ;;
        "macos")
            echo -e "${YELLOW}⚠️  theHarvester not available via brew, install manually if needed${NC}"
            ;;
        "arch")
            sudo pacman -S --noconfirm theharvester 2>/dev/null || {
                echo -e "${YELLOW}⚠️  theHarvester not available in repos, install manually if needed${NC}"
            }
            ;;
    esac
else
    echo -e "${GREEN}✅ theHarvester already installed${NC}"
fi

# Install Python dependencies
echo -e "\n${YELLOW}📦 Installing Python dependencies...${NC}"
if [[ -f "requirements.txt" ]]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found, installing essential dependencies${NC}"
    pip3 install toml colorama
fi

# Make script executable
echo -e "\n${YELLOW}🔧 Setting up BoxRecon...${NC}"
if [[ -f "boxrecon.py" ]]; then
    chmod +x boxrecon.py
    echo -e "${GREEN}✅ Made boxrecon.py executable${NC}"
else
    echo -e "${RED}❌ boxrecon.py not found in current directory${NC}"
    exit 1
fi

# Create wordlist directories if they don't exist
echo -e "\n${YELLOW}📁 Setting up wordlists...${NC}"

# Create multiple wordlist directories
WORDLIST_DIRS=("/usr/share/wordlists/dirb" "/usr/share/wordlists/dirbuster")

for dir in "${WORDLIST_DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        echo -e "${BLUE}🔄 Creating wordlist directory: $dir${NC}"
        sudo mkdir -p "$dir"
    fi
done

# Download HTB-optimized wordlists
DIRB_DIR="/usr/share/wordlists/dirb"
DIRBUSTER_DIR="/usr/share/wordlists/dirbuster"

# Download dirb wordlists
if [[ ! -f "$DIRB_DIR/common.txt" ]]; then
    echo -e "${BLUE}🔄 Downloading dirb common wordlist...${NC}"
    sudo wget -q https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt -O "$DIRB_DIR/common.txt"
    echo -e "${GREEN}✅ Downloaded dirb/common.txt${NC}"
fi

if [[ ! -f "$DIRB_DIR/big.txt" ]]; then
    echo -e "${BLUE}🔄 Downloading dirb big wordlist...${NC}"
    sudo wget -q https://raw.githubusercontent.com/v0re/dirb/master/wordlists/big.txt -O "$DIRB_DIR/big.txt"
    echo -e "${GREEN}✅ Downloaded dirb/big.txt${NC}"
fi

# Download dirbuster wordlists (HTB-optimized smaller lists)
if [[ ! -f "$DIRBUSTER_DIR/directory-list-2.3-small.txt" ]]; then
    echo -e "${BLUE}🔄 Downloading dirbuster small wordlist (HTB-optimized)...${NC}"
    sudo wget -q https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-2.3-small.txt -O "$DIRBUSTER_DIR/directory-list-2.3-small.txt" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Could not download dirbuster small wordlist, creating minimal list${NC}"
        sudo tee "$DIRBUSTER_DIR/directory-list-2.3-small.txt" > /dev/null << 'EOF'
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
index.php
admin.php
login.php
config.php
robots.txt
.htaccess
sitemap.xml
EOF
    }
    echo -e "${GREEN}✅ Set up dirbuster/directory-list-2.3-small.txt${NC}"
fi

# Verify installation
echo -e "\n${YELLOW}🔍 Verifying installation...${NC}"

TOOLS=("nmap" "gobuster" "nikto" "dnsrecon")
OPTIONAL_TOOLS=("feroxbuster" "ffuf" "theHarvester")
ALL_GOOD=true

for tool in "${TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}✅ $tool found${NC}"
    else
        echo -e "${RED}❌ $tool not found${NC}"
        ALL_GOOD=false
    fi
done

# Check optional tools
for tool in "${OPTIONAL_TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}✅ $tool found${NC}"
    else
        echo -e "${YELLOW}⚠️  $tool not found (optional)${NC}"
    fi
done

# Check WhatWeb separately
if command -v whatweb &> /dev/null; then
    echo -e "${GREEN}✅ whatweb found${NC}"
elif gem list whatweb | grep -q whatweb; then
    echo -e "${GREEN}✅ whatweb found (via gem)${NC}"
else
    echo -e "${YELLOW}⚠️  whatweb not found${NC}"
fi

# Test BoxRecon
echo -e "\n${YELLOW}🧪 Testing BoxRecon...${NC}"
if python3 boxrecon.py --version &> /dev/null; then
    echo -e "${GREEN}✅ BoxRecon is working correctly${NC}"
else
    echo -e "${RED}❌ BoxRecon test failed${NC}"
    ALL_GOOD=false
fi

# Final message
echo -e "\n${GREEN}🎉 Installation completed!${NC}"

if $ALL_GOOD; then
    echo -e "${GREEN}✅ All tools are ready to use${NC}"
    echo -e "\n${BLUE}🚀 To start BoxRecon, run:${NC}"
    echo -e "${YELLOW}   python3 boxrecon.py${NC}"
    echo -e "\n${CYAN}📋 Note: BoxRecon includes an ethical use disclaimer${NC}"
    echo -e "${CYAN}   You must agree to use the tool legally and ethically${NC}"
else
    echo -e "${YELLOW}⚠️  Some tools may not be available. Check the output above.${NC}"
    echo -e "${BLUE}💡 You can still use BoxRecon with the available tools.${NC}"
fi

echo -e "\n${BLUE}📖 For more information, check the README.md file${NC}"
echo -e "${GREEN}Happy hacking! 🎯${NC}"
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}BoxRecon created by hckerhub${NC}"
echo -e "${BLUE}🌐 Website: ${CYAN}https://hackerhub.me${NC}"
echo -e "${BLUE}🐦 X: ${CYAN}@hckerhub${NC}"
echo -e "${BLUE}☕ Support: ${CYAN}https://buymeacoffee.com/hckerhub${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" 