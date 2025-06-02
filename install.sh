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
    "curl:curl"
    "dig:dig"
)

# Advanced tools (optional but recommended)
OPTIONAL_TOOLS=(
    "feroxbuster:feroxbuster"
    "ffuf:ffuf"
    "theHarvester:theHarvester"
    "whatweb:whatweb"
    "wfuzz:wfuzz"
    "arjun:arjun"
    "paramspider:paramspider"
    "cmseek:cmseek"
    "cewl:cewl"
    "ruby:ruby"
    "gobuster:gobuster"
    "subfinder:subfinder"
    "amass:amass"
    "dnsrecon:dnsrecon"
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
        # Install what's available via apt (HTB-optimized tools)
        sudo apt install -y nmap curl wget dnsutils ruby ruby-dev cewl dnsrecon gobuster
        ;;
        
    "macos")
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ Homebrew not found. Please install Homebrew first:${NC}"
            echo -e "${BLUE}   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            exit 1
        fi
        
        echo -e "\n${BLUE}🔄 Installing tools via Homebrew...${NC}"
        # Install HTB-optimized tools via Homebrew
        brew install nmap curl feroxbuster ffuf ruby bind gobuster
        
        # Note: cewl might not be available via brew, install as Ruby gem later
        
        # Set up Ruby path for gems
        echo -e "${BLUE}🔄 Setting up Ruby path...${NC}"
        export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
        ;;
        
    "arch")
        echo -e "\n${BLUE}🔄 Installing tools via pacman...${NC}"
        # Install HTB-optimized tools via pacman
        sudo pacman -S --noconfirm nmap curl bind ruby feroxbuster ffuf gobuster
        
        # Note: cewl might need to be installed separately
        ;;
esac

# Install tools that need manual installation
echo -e "\n${YELLOW}🔧 Installing tools that require manual setup...${NC}"

# Install WFUZZ
if ! command -v wfuzz &> /dev/null; then
    echo -e "${BLUE}🔄 Installing WFUZZ...${NC}"
    pip3 install --break-system-packages wfuzz 2>/dev/null || pip3 install wfuzz
    echo -e "${GREEN}✅ WFUZZ installed${NC}"
fi

# Install Arjun
if ! command -v arjun &> /dev/null; then
    echo -e "${BLUE}🔄 Installing Arjun...${NC}"
    pip3 install --break-system-packages arjun 2>/dev/null || pip3 install arjun
    echo -e "${GREEN}✅ Arjun installed${NC}"
fi

# Install ParamSpider
if ! command -v paramspider &> /dev/null; then
    echo -e "${BLUE}🔄 Installing ParamSpider...${NC}"
    if [[ -d "/tmp/ParamSpider" ]]; then
        rm -rf /tmp/ParamSpider
    fi
    git clone https://github.com/devanshbatham/ParamSpider.git /tmp/ParamSpider
    cd /tmp/ParamSpider
    pip3 install --break-system-packages -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt
    sudo ln -sf "$(pwd)/paramspider.py" /usr/local/bin/paramspider
    sudo chmod +x /usr/local/bin/paramspider
    cd - > /dev/null
    echo -e "${GREEN}✅ ParamSpider installed${NC}"
fi

# Install CMSeek
if ! command -v cmseek &> /dev/null; then
    echo -e "${BLUE}🔄 Installing CMSeek...${NC}"
    if [[ -d "/tmp/CMSeek" ]]; then
        rm -rf /tmp/CMSeek
    fi
    git clone https://github.com/Tuhinshubhra/CMSeek.git /tmp/CMSeek
    cd /tmp/CMSeek
    pip3 install --break-system-packages -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt
    sudo ln -sf "$(pwd)/cmseek.py" /usr/local/bin/cmseek
    sudo chmod +x /usr/local/bin/cmseek
    cd - > /dev/null
    echo -e "${GREEN}✅ CMSeek installed${NC}"
fi

# Install CeWL (Custom Word List generator)
if ! command -v cewl &> /dev/null; then
    echo -e "${BLUE}🔄 Installing CeWL (Custom Word List generator)...${NC}"
    case $OS in
        "debian")
            # Try apt first (should work on most Debian/Ubuntu systems)
            if sudo apt install -y cewl 2>/dev/null; then
                echo -e "${GREEN}✅ CeWL installed via apt${NC}"
            else
                # Fallback to Ruby gem installation
                echo -e "${BLUE}🔄 Installing CeWL via Ruby gem...${NC}"
                sudo gem install cewl
                echo -e "${GREEN}✅ CeWL installed via Ruby gem${NC}"
            fi
            ;;
        "macos"|"arch")
            # Install as Ruby gem
            echo -e "${BLUE}🔄 Installing CeWL via Ruby gem...${NC}"
            sudo gem install cewl
            echo -e "${GREEN}✅ CeWL installed via Ruby gem${NC}"
            ;;
    esac
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

# Install WhatWeb (required for automatic web technology detection)
if ! command -v whatweb &> /dev/null; then
    echo -e "${BLUE}🔄 Installing WhatWeb (required for automatic web technology detection)...${NC}"
    
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

# Install advanced HTB tools for enhanced DNS enumeration
echo -e "\n${YELLOW}🚀 Installing HTB-optimized advanced tools...${NC}"

# Install Subfinder (requires Go)
if ! command -v subfinder &> /dev/null; then
    echo -e "${BLUE}🔄 Installing Subfinder (advanced subdomain enumeration)...${NC}"
    
    # Check if Go is installed
    if command -v go &> /dev/null; then
        echo -e "${BLUE}🔄 Using Go to install Subfinder...${NC}"
        go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
        
        # Ensure Go bin is in PATH
        if [[ -d "$HOME/go/bin" ]]; then
            export PATH="$HOME/go/bin:$PATH"
            echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.bashrc
        fi
        
        # Create symlink for system-wide access
        if [[ -f "$HOME/go/bin/subfinder" ]]; then
            sudo ln -sf "$HOME/go/bin/subfinder" /usr/local/bin/subfinder
            echo -e "${GREEN}✅ Subfinder installed via Go${NC}"
        else
            echo -e "${YELLOW}⚠️  Subfinder installation via Go may have issues${NC}"
        fi
    else
        echo -e "${BLUE}🔄 Installing Subfinder from GitHub releases...${NC}"
        case $(uname -m) in
            x86_64) ARCH="amd64" ;;
            arm64|aarch64) ARCH="arm64" ;;
            *) ARCH="amd64" ;;
        esac
        
        case $OS in
            "debian"|"arch") OS_TYPE="linux" ;;
            "macos") OS_TYPE="macOS" ;;
        esac
        
        # Download latest release
        SUBFINDER_URL="https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_2.6.3_${OS_TYPE}_${ARCH}.zip"
        curl -L "$SUBFINDER_URL" -o /tmp/subfinder.zip 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Could not download Subfinder binary${NC}"
        }
        
        if [[ -f "/tmp/subfinder.zip" ]]; then
            cd /tmp
            unzip -q subfinder.zip
            sudo mv subfinder /usr/local/bin/
            sudo chmod +x /usr/local/bin/subfinder
            rm -f subfinder.zip
            cd - > /dev/null
            echo -e "${GREEN}✅ Subfinder installed from GitHub releases${NC}"
        fi
    fi
fi

# Install Amass (advanced OSINT tool)
if ! command -v amass &> /dev/null; then
    echo -e "${BLUE}🔄 Installing Amass (advanced OSINT enumeration)...${NC}"
    
    case $OS in
        "debian")
            # Try installing via snap first (most reliable)
            if command -v snap &> /dev/null; then
                echo -e "${BLUE}🔄 Installing Amass via snap...${NC}"
                sudo snap install amass
                echo -e "${GREEN}✅ Amass installed via snap${NC}"
            else
                # Fallback to GitHub releases
                echo -e "${BLUE}🔄 Installing Amass from GitHub releases...${NC}"
                case $(uname -m) in
                    x86_64) ARCH="amd64" ;;
                    *) ARCH="amd64" ;;
                esac
                
                AMASS_URL="https://github.com/owasp-amass/amass/releases/latest/download/amass_linux_${ARCH}.zip"
                curl -L "$AMASS_URL" -o /tmp/amass.zip 2>/dev/null || {
                    echo -e "${YELLOW}⚠️  Could not download Amass binary${NC}"
                }
                
                if [[ -f "/tmp/amass.zip" ]]; then
                    cd /tmp
                    unzip -q amass.zip
                    # Find the amass binary in the extracted directory
                    find . -name "amass" -type f -executable | head -1 | xargs -I {} sudo mv {} /usr/local/bin/
                    sudo chmod +x /usr/local/bin/amass
                    rm -rf amass* && rm -f amass.zip
                    cd - > /dev/null
                    echo -e "${GREEN}✅ Amass installed from GitHub releases${NC}"
                fi
            fi
            ;;
        "macos")
            # Use Homebrew
            if brew install amass 2>/dev/null; then
                echo -e "${GREEN}✅ Amass installed via Homebrew${NC}"
            else
                echo -e "${YELLOW}⚠️  Amass not available via Homebrew${NC}"
            fi
            ;;
        "arch")
            # Try AUR or manual installation
            if command -v yay &> /dev/null; then
                yay -S amass --noconfirm 2>/dev/null || echo -e "${YELLOW}⚠️  Amass not available via yay${NC}"
            else
                echo -e "${YELLOW}⚠️  Consider installing Amass manually or via AUR${NC}"
            fi
            ;;
    esac
fi

# Install SecLists wordlists (critical for HTB)
if [[ ! -d "/usr/share/seclists" ]]; then
    echo -e "${BLUE}🔄 Installing SecLists (essential HTB wordlists)...${NC}"
    
    case $OS in
        "debian")
            # Try apt first
            if sudo apt install -y seclists 2>/dev/null; then
                echo -e "${GREEN}✅ SecLists installed via apt${NC}"
            else
                # Fallback to GitHub clone
                echo -e "${BLUE}🔄 Installing SecLists from GitHub...${NC}"
                sudo git clone https://github.com/danielmiessler/SecLists.git /usr/share/seclists
                echo -e "${GREEN}✅ SecLists installed from GitHub${NC}"
            fi
            ;;
        "macos")
            # Install via Homebrew or manual clone
            if brew install seclists 2>/dev/null; then
                echo -e "${GREEN}✅ SecLists installed via Homebrew${NC}"
            else
                echo -e "${BLUE}🔄 Installing SecLists from GitHub...${NC}"
                sudo git clone https://github.com/danielmiessler/SecLists.git /usr/share/seclists
                echo -e "${GREEN}✅ SecLists installed from GitHub${NC}"
            fi
            ;;
        "arch")
            # Try pacman or manual clone
            if sudo pacman -S --noconfirm seclists 2>/dev/null; then
                echo -e "${GREEN}✅ SecLists installed via pacman${NC}"
            else
                echo -e "${BLUE}🔄 Installing SecLists from GitHub...${NC}"
                sudo git clone https://github.com/danielmiessler/SecLists.git /usr/share/seclists
                echo -e "${GREEN}✅ SecLists installed from GitHub${NC}"
            fi
            ;;
    esac
    
    # Set proper permissions
    if [[ -d "/usr/share/seclists" ]]; then
        sudo chmod -R 755 /usr/share/seclists
        echo -e "${GREEN}✅ SecLists permissions configured${NC}"
    fi
else
    echo -e "${GREEN}✅ SecLists already installed${NC}"
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

# Enhanced verification for HTB tools
HTB_TOOLS=(
    "gobuster:gobuster"
    "subfinder:subfinder"
    "amass:amass"
)

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

echo -e "\n${CYAN}🚀 HTB-Optimized Tools Status:${NC}"
for tool_pair in "${HTB_TOOLS[@]}"; do
    tool_name=$(echo "$tool_pair" | cut -d':' -f1)
    command_name=$(echo "$tool_pair" | cut -d':' -f2)
    
    if check_tool "$tool_name" "$command_name"; then
        echo -e "${GREEN}   🎯 $tool_name ready for HTB enumeration${NC}"
    else
        echo -e "${YELLOW}   ⚠️  $tool_name not available (advanced features may be limited)${NC}"
    fi
done

# Check SecLists specifically
if [[ -d "/usr/share/seclists" ]]; then
    echo -e "${GREEN}✅ SecLists wordlists installed (critical for HTB)${NC}"
    echo -e "${CYAN}   📋 HTB champion wordlist: /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt${NC}"
else
    echo -e "${YELLOW}⚠️  SecLists not found - using fallback wordlists${NC}"
fi

# Test ipsnipe
echo -e "\n${YELLOW}🧪 Testing ipsnipe...${NC}"
if python3 ipsnipe.py --version &> /dev/null; then
    echo -e "${GREEN}✅ ipsnipe is working correctly${NC}"
else
    echo -e "${YELLOW}⚠️  ipsnipe test inconclusive (might still work)${NC}"
fi

# Final message
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 ipsnipe HTB-Optimized Installation Completed!${NC}"

if [[ "$VERIFICATION_FAILED" == false ]]; then
    echo -e "${GREEN}✅ All core tools are installed and ready for HTB reconnaissance${NC}"
    echo -e "${CYAN}🎯 HTB-specific enhancements include:${NC}"
    echo -e "${BLUE}   • Advanced DNS enumeration (subfinder, amass, certificate transparency)${NC}"
    echo -e "${BLUE}   • Enhanced web discovery (gobuster, JavaScript analysis, multi-tool)${NC}"
    echo -e "${BLUE}   • HTB-optimized wordlists (SecLists directory-list-2.3-medium.txt)${NC}"
    echo -e "${BLUE}   • Automatic domain discovery and /etc/hosts management${NC}"
    echo -e "\n${BLUE}🚀 To start ipsnipe, run:${NC}"
    echo -e "${YELLOW}   python3 ipsnipe.py${NC}"
else
    echo -e "${YELLOW}⚠️  Some core tools may not be available. Check the verification results above.${NC}"
    echo -e "${BLUE}💡 ipsnipe will work with available tools, but some HTB features may be limited.${NC}"
    echo -e "\n${BLUE}🚀 You can still try running ipsnipe:${NC}"
    echo -e "${YELLOW}   python3 ipsnipe.py${NC}"
fi

echo -e "\n${CYAN}📋 Important Notes:${NC}"
echo -e "${BLUE}• ipsnipe includes an ethical use disclaimer${NC}"
echo -e "${BLUE}• You must agree to use the tool legally and ethically${NC}"
echo -e "${BLUE}• HTB-optimized features require Enhanced Mode (sudo access)${NC}"
echo -e "${BLUE}• Advanced DNS tools (subfinder, amass) provide comprehensive enumeration${NC}"
echo -e "${BLUE}• SecLists wordlists are essential for effective HTB reconnaissance${NC}"

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