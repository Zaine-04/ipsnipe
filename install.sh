#!/bin/bash

# ipsnipe Installation Script
# Supports Ubuntu/Debian, macOS, and Kali Linux

set -e

# Setup PATH for different operating systems
case "$OSTYPE" in
    "darwin"*)
        # macOS: Add Homebrew paths (auto-detect installation)
        for brew_path in "/opt/homebrew" "/usr/local"; do
            [[ -d "$brew_path/bin" ]] && export PATH="$brew_path/bin:$PATH"
        done
        ;;
    "linux-gnu"*)
        # Linux: Add standard binary paths
        [[ -d "/usr/local/bin" ]] && export PATH="/usr/local/bin:$PATH"
        [[ -d "/usr/bin" ]] && export PATH="/usr/bin:$PATH"
        ;;
esac

# Add user-installed packages to PATH (universal)
[[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"
[[ -d "$HOME/go/bin" ]] && export PATH="$HOME/go/bin:$PATH"

# Add Python user site packages to PATH
if command -v python3 &> /dev/null; then
    USER_BASE=$(python3 -m site --user-base 2>/dev/null) && [[ -d "$USER_BASE/bin" ]] && export PATH="$USER_BASE/bin:$PATH"
fi

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
    # Store the original Python executable before any PATH modifications
    PYTHON_EXEC=$(command -v python3)
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python 3 found: $PYTHON_VERSION${NC}"
    echo -e "${BLUE}📍 Using Python: $PYTHON_EXEC${NC}"
    
    # Show if this is different from system default (detect Homebrew dynamically)
    SYSTEM_PYTHON=""
    for brew_path in "/opt/homebrew" "/usr/local"; do
        if [[ -f "$brew_path/bin/python3" ]]; then
            SYSTEM_PYTHON="$brew_path/bin/python3"
            break
        fi
    done
    
    if [[ -n "$SYSTEM_PYTHON" ]] && [[ "$PYTHON_EXEC" != "$SYSTEM_PYTHON" ]]; then
        SYSTEM_VERSION=$($SYSTEM_PYTHON --version | cut -d' ' -f2)
        echo -e "${CYAN}ℹ️  System Python: $SYSTEM_PYTHON ($SYSTEM_VERSION)${NC}"
        echo -e "${CYAN}ℹ️  Using PATH-priority Python for consistency${NC}"
    fi
    
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

# Advanced tools (required for full functionality)
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

echo -e "\n${CYAN}🔍 Required Tools Status:${NC}"
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

if ! python3 -c "import rich" &> /dev/null; then
    echo -e "${RED}❌ Python package 'rich' not found${NC}"
    PYTHON_DEPS_MISSING=true
else
    echo -e "${GREEN}✅ Python package 'rich' found${NC}"
fi

if ! python3 -c "import requests" &> /dev/null; then
    echo -e "${RED}❌ Python package 'requests' not found${NC}"
    PYTHON_DEPS_MISSING=true
else
    echo -e "${GREEN}✅ Python package 'requests' found${NC}"
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
    echo -e "${GREEN}✅ All required tools are already installed${NC}"
else
    echo -e "${RED}❌ Missing required tools: ${#MISSING_OPTIONAL[@]}${NC}"
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
if [[ "$NEEDS_INSTALLATION" == true ]]; then
    echo -e "\n${YELLOW}📋 Installation Summary:${NC}"
    
    # Show what's already installed
    INSTALLED_CORE=()
    INSTALLED_OPTIONAL=()
    
    for tool_pair in "${CORE_TOOLS[@]}"; do
        tool_name=$(echo "$tool_pair" | cut -d':' -f1)
        command_name=$(echo "$tool_pair" | cut -d':' -f2)
        if command -v "$command_name" &> /dev/null; then
            INSTALLED_CORE+=("$tool_name")
        fi
    done
    
    for tool_pair in "${OPTIONAL_TOOLS[@]}"; do
        tool_name=$(echo "$tool_pair" | cut -d':' -f1)
        command_name=$(echo "$tool_pair" | cut -d':' -f2)
        if command -v "$command_name" &> /dev/null; then
            INSTALLED_OPTIONAL+=("$tool_name")
        fi
    done
    
    # Show already installed tools
    if [[ ${#INSTALLED_CORE[@]} -gt 0 || ${#INSTALLED_OPTIONAL[@]} -gt 0 ]]; then
        echo -e "\n${GREEN}✅ Already installed:${NC}"
        for tool in "${INSTALLED_CORE[@]}"; do
            echo -e "   ${GREEN}• $tool (core)${NC}"
        done
        for tool in "${INSTALLED_OPTIONAL[@]}"; do
            echo -e "   ${GREEN}• $tool (advanced)${NC}"
        done
    fi
    
    # Show what needs to be installed
    echo -e "\n${CYAN}📦 Need to install:${NC}"
    
    if [[ ${#MISSING_CORE[@]} -gt 0 ]]; then
        echo -e "${RED}🔧 Core tools (required):${NC}"
        for tool_pair in "${MISSING_CORE[@]}"; do
            tool_name=$(echo "$tool_pair" | cut -d':' -f1)
            echo -e "   ${RED}• $tool_name${NC}"
        done
    fi

    if [[ ${#MISSING_OPTIONAL[@]} -gt 0 ]]; then
        echo -e "${CYAN}🔧 Advanced tools (required):${NC}"
        for tool_pair in "${MISSING_OPTIONAL[@]}"; do
            tool_name=$(echo "$tool_pair" | cut -d':' -f1)
            echo -e "   ${CYAN}• $tool_name${NC}"
        done
    fi

    if [[ "$PYTHON_DEPS_MISSING" == true ]]; then
        echo -e "${BLUE}🐍 Python packages:${NC}"
        echo -e "   ${BLUE}• toml, rich, requests${NC}"
    fi
    
    # Calculate totals
    TOTAL_TOOLS=$((${#CORE_TOOLS[@]} + ${#OPTIONAL_TOOLS[@]}))
    INSTALLED_TOOLS=$((${#INSTALLED_CORE[@]} + ${#INSTALLED_OPTIONAL[@]}))
    MISSING_TOOLS=$((${#MISSING_CORE[@]} + ${#MISSING_OPTIONAL[@]}))
    
    echo -e "\n${YELLOW}📊 Status: ${INSTALLED_TOOLS}/${TOTAL_TOOLS} tools installed${NC}"
    if [[ "$PYTHON_DEPS_MISSING" == true ]]; then
        echo -e "${YELLOW}📊 Python dependencies need installation${NC}"
    else
        echo -e "${GREEN}📊 Python dependencies are ready${NC}"
    fi

    echo -e "\n${YELLOW}❓ Do you want to proceed with installing the missing tools? (y/N): ${NC}"
    read -r RESPONSE

    if [[ ! "$RESPONSE" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}💡 Installation cancelled.${NC}"
        echo -e "${YELLOW}📋 ipsnipe will work with available tools, but some features may be limited.${NC}"
        echo -e "${BLUE}🚀 You can still try running: ${YELLOW}python3 ipsnipe.py${NC}"
        echo -e "\n${YELLOW}Press Enter to close the terminal...${NC}"
        read -r
        exit 0
    fi

    echo -e "\n${GREEN}🚀 Starting installation of missing tools...${NC}"
fi

# Install Python dependencies first
if [[ "$PYTHON_DEPS_MISSING" == true ]]; then
    echo -e "\n${YELLOW}🐍 Installing Python dependencies...${NC}"
    
    # Use the Python executable detected earlier (no need to re-detect)
    echo -e "${BLUE}📍 Using Python: $PYTHON_EXEC${NC}"
    
    # Try to install pipx first if it's not available (for better tool isolation)
    if ! command -v pipx &> /dev/null; then
        echo -e "${BLUE}🔄 Installing pipx for isolated tool installations...${NC}"
        if $PYTHON_EXEC -m pip install --user pipx &> /dev/null; then
            echo -e "${GREEN}✅ pipx installed${NC}"
            # Ensure pipx is in PATH
            export PATH="$HOME/.local/bin:$PATH"
            # Initialize pipx if needed
            if command -v pipx &> /dev/null; then
                pipx ensurepath &> /dev/null || true
            fi
        elif pip3 install --break-system-packages pipx &> /dev/null; then
            echo -e "${GREEN}✅ pipx installed (system)${NC}"
            export PATH="$HOME/.local/bin:$PATH"
        else
            echo -e "${BLUE}ℹ️  pipx installation failed - will use alternative methods${NC}"
        fi
    fi
    
    if [[ -f "requirements.txt" ]]; then
        # Try different methods for installing Python packages
        echo -e "${BLUE}🔄 Trying requirements.txt installation...${NC}"
        if $PYTHON_EXEC -m pip install --user -r requirements.txt &> /dev/null; then
            echo -e "${GREEN}✅ Python dependencies installed (user mode)${NC}"
        elif $PYTHON_EXEC -m pip install --break-system-packages -r requirements.txt &> /dev/null; then
            echo -e "${GREEN}✅ Python dependencies installed (system packages)${NC}"
        elif pip3 install --user -r requirements.txt &> /dev/null; then
            echo -e "${GREEN}✅ Python dependencies installed (user mode via pip3)${NC}"
        elif pip3 install --break-system-packages -r requirements.txt &> /dev/null; then
            echo -e "${GREEN}✅ Python dependencies installed (system packages via pip3)${NC}"
        else
            echo -e "${YELLOW}⚠️  Installing essential Python packages individually...${NC}"
            # Try with python3 -m pip first, then fallback to pip3
            if ! $PYTHON_EXEC -m pip install --user toml rich requests &> /dev/null; then
                if ! $PYTHON_EXEC -m pip install --break-system-packages toml rich requests &> /dev/null; then
                    pip3 install --break-system-packages toml rich requests || {
                        echo -e "${RED}❌ Failed to install Python dependencies${NC}"
                        echo -e "${YELLOW}💡 You may need to install them manually:${NC}"
                        echo -e "${YELLOW}   $PYTHON_EXEC -m pip install --user toml rich requests${NC}"
                        echo -e "${YELLOW}   OR: pip3 install --break-system-packages toml rich requests${NC}"
                    }
                fi
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  requirements.txt not found, installing essential dependencies${NC}"
        # Try with python3 -m pip first, then fallback to pip3
        if ! $PYTHON_EXEC -m pip install --user toml rich requests &> /dev/null; then
            if ! $PYTHON_EXEC -m pip install --break-system-packages toml rich requests &> /dev/null; then
                pip3 install --break-system-packages toml rich requests || {
                    echo -e "${RED}❌ Failed to install Python dependencies${NC}"
                    echo -e "${YELLOW}💡 You may need to install them manually:${NC}"
                    echo -e "${YELLOW}   $PYTHON_EXEC -m pip install --user toml rich requests${NC}"
                }
            fi
        fi
    fi
    
    # Verify installation worked
    echo -e "${BLUE}🔍 Verifying Python dependencies installation...${NC}"
    VERIFICATION_FAILED=false
    
    for package in toml rich requests; do
        if $PYTHON_EXEC -c "import $package" &> /dev/null; then
            echo -e "${GREEN}✅ $package verified${NC}"
        else
            echo -e "${RED}❌ $package verification failed${NC}"
            VERIFICATION_FAILED=true
        fi
    done
    
    if [[ "$VERIFICATION_FAILED" == true ]]; then
        echo -e "${YELLOW}⚠️  Some Python packages may not have installed correctly${NC}"
        echo -e "${BLUE}💡 Try running: $PYTHON_EXEC -m pip install --user toml rich requests${NC}"
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
        # Check for Homebrew
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ Homebrew not found. Please install Homebrew first:${NC}"
            echo -e "${BLUE}   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            echo -e "${YELLOW}💡 After installing, you may need to restart your terminal${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Homebrew found${NC}"
        echo -e "\n${BLUE}🔄 Installing tools via Homebrew...${NC}"
        # Install HTB-optimized tools via Homebrew
        brew install nmap curl feroxbuster ffuf ruby bind gobuster
        
        # Note: cewl might not be available via brew, install as Ruby gem later
        
        # Set up Ruby path for gems (auto-detect Homebrew)
        echo -e "${BLUE}🔄 Setting up Ruby path...${NC}"
        for brew_path in "/opt/homebrew" "/usr/local"; do
            if [[ -d "$brew_path/opt/ruby/bin" ]]; then
                export PATH="$brew_path/opt/ruby/bin:$PATH"
                break
            fi
        done
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

# Debug: Show current PATH
echo -e "${BLUE}🔍 Debug: Current PATH includes:${NC}"
echo "$PATH" | tr ':' '\n' | head -5 | sed 's/^/  /'

# Install modern web fuzzing tools (ffuf/feroxbuster replace wfuzz)
echo -e "${BLUE}🔍 Installing modern web fuzzing tools...${NC}"

# Check if we have any web fuzzing tool available
FUZZING_TOOLS_AVAILABLE=false

# Check feroxbuster (already installed via package manager)
if command -v feroxbuster &> /dev/null; then
    echo -e "${GREEN}✅ feroxbuster already available${NC}"
    FUZZING_TOOLS_AVAILABLE=true
fi

# Install ffuf as modern wfuzz alternative
if ! command -v ffuf &> /dev/null; then
    echo -e "${BLUE}🔄 Installing ffuf (modern wfuzz alternative)...${NC}"
    
    FFUF_INSTALLED=false
    
    # Method 1: Homebrew (preferred for macOS)
    if command -v brew &> /dev/null; then
        if brew install ffuf &> /dev/null; then
            FFUF_INSTALLED=true
            echo -e "${GREEN}✅ ffuf installed via Homebrew${NC}"
        fi
    fi
    
    # Method 2: Go installation (if Go is available)
    if [[ "$FFUF_INSTALLED" == false ]] && command -v go &> /dev/null; then
        if go install github.com/ffuf/ffuf@latest &> /dev/null; then
            # Add Go bin to PATH if not already there
            if [[ ":$PATH:" != *":$HOME/go/bin:"* ]]; then
                export PATH="$HOME/go/bin:$PATH"
                echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.zshrc 2>/dev/null || echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.bash_profile 2>/dev/null
            fi
            FFUF_INSTALLED=true
            echo -e "${GREEN}✅ ffuf installed via Go${NC}"
        fi
    fi
    
    # Method 3: Direct binary download (fallback for macOS)
    if [[ "$FFUF_INSTALLED" == false ]] && [[ "$OSTYPE" == "darwin"* ]]; then
        ARCH=$(uname -m)
        if [[ "$ARCH" == "arm64" ]]; then
            BINARY_URL="https://github.com/ffuf/ffuf/releases/latest/download/ffuf_2.1.0_darwin_arm64.tar.gz"
        else
            BINARY_URL="https://github.com/ffuf/ffuf/releases/latest/download/ffuf_2.1.0_darwin_amd64.tar.gz"
        fi
        
        if curl -L "$BINARY_URL" -o /tmp/ffuf.tar.gz &> /dev/null && cd /tmp && tar -xzf ffuf.tar.gz &> /dev/null; then
            mkdir -p "$HOME/.local/bin"
            mv ffuf "$HOME/.local/bin/" 2>/dev/null
            chmod +x "$HOME/.local/bin/ffuf"
            export PATH="$HOME/.local/bin:$PATH"
            FFUF_INSTALLED=true
            echo -e "${GREEN}✅ ffuf installed via binary download${NC}"
            cd - > /dev/null
        fi
    fi
    
    if [[ "$FFUF_INSTALLED" == true ]]; then
        FUZZING_TOOLS_AVAILABLE=true
    else
        echo -e "${BLUE}ℹ️  ffuf installation skipped (will use feroxbuster)${NC}"
    fi
else
    echo -e "${GREEN}✅ ffuf already available${NC}"
    FUZZING_TOOLS_AVAILABLE=true
fi

# Install wfuzz (with macOS-aware installation)
if ! command -v wfuzz &> /dev/null; then
    echo -e "${BLUE}🔄 Installing wfuzz...${NC}"
    
    WFUZZ_INSTALLED=false
    
    # OS-specific installation approach
    if [[ "$OS" == "debian" ]]; then
        # For Debian/Ubuntu/Parrot OS - try apt first, then pip
        if sudo apt install -y wfuzz &> /dev/null; then
            WFUZZ_INSTALLED=true
            echo -e "${GREEN}✅ wfuzz installed via apt${NC}"
        elif pip3 install --break-system-packages wfuzz &> /dev/null; then
            WFUZZ_INSTALLED=true
            echo -e "${GREEN}✅ wfuzz installed via pip3 (system packages)${NC}"
        elif pip3 install wfuzz &> /dev/null; then
            WFUZZ_INSTALLED=true
            echo -e "${GREEN}✅ wfuzz installed via pip3${NC}"
        fi
    elif [[ "$OS" == "macos" ]]; then
        # macOS-specific wfuzz installation (handles pycurl SSL issues)
        echo -e "${BLUE}🔄 Installing wfuzz with macOS SSL fixes...${NC}"
        
        # Step 1: Ensure OpenSSL is available
        if ! command -v openssl &> /dev/null || ! brew list openssl &> /dev/null; then
            echo -e "${BLUE}🔄 Installing OpenSSL...${NC}"
            brew install openssl &> /dev/null || true
        fi
        
        # Step 2: Ensure curl-openssl is available
        if ! brew list curl-openssl &> /dev/null 2>&1; then
            echo -e "${BLUE}🔄 Installing curl-openssl...${NC}"
            brew install curl-openssl &> /dev/null || true
        fi
        
        # Step 3: Set up SSL environment and install pycurl properly
        if ! python3 -c "import pycurl" &> /dev/null; then
            echo -e "${BLUE}🔄 Installing pycurl with SSL support...${NC}"
            # Auto-detect Homebrew paths
            HOMEBREW_PREFIX=""
            for brew_path in "/opt/homebrew" "/usr/local"; do
                if [[ -d "$brew_path" ]]; then
                    HOMEBREW_PREFIX="$brew_path"
                    break
                fi
            done
            
            if [[ -n "$HOMEBREW_PREFIX" ]]; then
                export PATH="$HOMEBREW_PREFIX/opt/curl-openssl/bin:$PATH"
                PYCURL_SSL_LIBRARY=openssl \
                LDFLAGS="-L$HOMEBREW_PREFIX/opt/openssl/lib" \
                CPPFLAGS="-I$HOMEBREW_PREFIX/opt/openssl/include" \
                pip3 install --no-cache-dir pycurl &> /dev/null || true
            fi
        fi
        
        # Step 4: Install wfuzz with proper environment
        HOMEBREW_PREFIX=""
        for brew_path in "/opt/homebrew" "/usr/local"; do
            if [[ -d "$brew_path" ]]; then
                HOMEBREW_PREFIX="$brew_path"
                break
            fi
        done
        [[ -n "$HOMEBREW_PREFIX" ]] && export PATH="$HOMEBREW_PREFIX/opt/curl-openssl/bin:$PATH"
        if pip3 install wfuzz &> /dev/null; then
            WFUZZ_INSTALLED=true
            echo -e "${GREEN}✅ wfuzz installed via pip3 (macOS SSL fixed)${NC}"
        elif python3 -m pip install --user wfuzz &> /dev/null; then
            WFUZZ_INSTALLED=true
            echo -e "${GREEN}✅ wfuzz installed via python3 -m pip (user)${NC}"
            [[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"
        fi
    else
        # For other OS - use standard pip methods
        if pip3 install wfuzz &> /dev/null; then
            WFUZZ_INSTALLED=true
            echo -e "${GREEN}✅ wfuzz installed via pip3${NC}"
        elif python3 -m pip install --user wfuzz &> /dev/null; then
            WFUZZ_INSTALLED=true
            echo -e "${GREEN}✅ wfuzz installed via python3 -m pip (user)${NC}"
            [[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"
        fi
    fi
    
    if [[ "$WFUZZ_INSTALLED" == false ]]; then
        echo -e "${YELLOW}⚠️  wfuzz installation failed (likely pycurl SSL issues on macOS)${NC}"
        echo -e "${GREEN}✅ ffuf and feroxbuster provide modern alternatives${NC}"
        echo -e "${BLUE}💡 wfuzz requires complex SSL setup on macOS - using modern tools instead${NC}"
    fi
else
    echo -e "${GREEN}✅ wfuzz already installed${NC}"
    # Check if it's working properly
    if ! wfuzz --version &> /dev/null; then
        echo -e "${YELLOW}⚠️  wfuzz command exists but appears broken - attempting macOS SSL fix...${NC}"
        
        # Remove any broken wrappers
        rm -f "$HOME/.local/bin/wfuzz" 2>/dev/null
        
        # Try to fix wfuzz on macOS
        if [[ "$OS" == "macos" ]]; then
            echo -e "${BLUE}🔄 Applying macOS SSL fixes for wfuzz...${NC}"
            
            # Ensure SSL libraries are available
            brew install openssl curl-openssl &> /dev/null || true
            
            # Reinstall pycurl with proper SSL (auto-detect Homebrew)
            pip3 uninstall -y pycurl &> /dev/null || true
            HOMEBREW_PREFIX=""
            for brew_path in "/opt/homebrew" "/usr/local"; do
                if [[ -d "$brew_path" ]]; then
                    HOMEBREW_PREFIX="$brew_path"
                    break
                fi
            done
            
            if [[ -n "$HOMEBREW_PREFIX" ]]; then
                export PATH="$HOMEBREW_PREFIX/opt/curl-openssl/bin:$PATH"
                PYCURL_SSL_LIBRARY=openssl \
                LDFLAGS="-L$HOMEBREW_PREFIX/opt/openssl/lib" \
                CPPFLAGS="-I$HOMEBREW_PREFIX/opt/openssl/include" \
                pip3 install --no-cache-dir pycurl &> /dev/null || true
            fi
            
            # Reinstall wfuzz
            if pip3 install --force-reinstall wfuzz &> /dev/null; then
                echo -e "${GREEN}✅ wfuzz fixed with macOS SSL configuration${NC}"
            else
                echo -e "${YELLOW}⚠️  wfuzz macOS SSL fix failed - using ffuf/feroxbuster instead${NC}"
            fi
        elif [[ "$OS" == "debian" ]]; then
            if sudo apt install -y --reinstall wfuzz &> /dev/null; then
                echo -e "${GREEN}✅ wfuzz reinstalled via apt${NC}"
            elif pip3 install --break-system-packages --force-reinstall wfuzz &> /dev/null; then
                echo -e "${GREEN}✅ wfuzz reinstalled via pip3${NC}"
            else
                echo -e "${YELLOW}⚠️  wfuzz reinstallation failed - using ffuf/feroxbuster instead${NC}"
            fi
        else
            if pip3 install --force-reinstall wfuzz &> /dev/null; then
                echo -e "${GREEN}✅ wfuzz reinstalled via pip3${NC}"
            else
                echo -e "${YELLOW}⚠️  wfuzz reinstallation failed - using ffuf/feroxbuster instead${NC}"
            fi
        fi
    fi
fi

# Status summary for web fuzzing tools
if [[ "$FUZZING_TOOLS_AVAILABLE" == true ]]; then
    echo -e "${GREEN}✅ Web fuzzing tools available (feroxbuster/ffuf)${NC}"
else
    echo -e "${YELLOW}⚠️  No web fuzzing tools available - install Go or Homebrew for ffuf${NC}"
fi

# Install Arjun (required tool)
if ! command -v arjun &> /dev/null; then
    echo -e "${BLUE}🔄 Installing Arjun...${NC}"
    
    ARJUN_INSTALLED=false
    
    # OS-specific installation approach
    case "$OS" in
        "macos")
            # Method 1: Homebrew (preferred for macOS) - v2.2.7 available
            if command -v brew &> /dev/null; then
                if brew install arjun &> /dev/null; then
                    ARJUN_INSTALLED=true
                    echo -e "${GREEN}✅ Arjun installed via Homebrew${NC}"
                fi
            fi
            
            # Method 2: pipx fallback
            if [[ "$ARJUN_INSTALLED" == false ]] && command -v pipx &> /dev/null; then
                if pipx install arjun &> /dev/null; then
                    ARJUN_INSTALLED=true
                    echo -e "${GREEN}✅ Arjun installed via pipx${NC}"
                fi
            fi
            
            # Method 3: pip fallback
            if [[ "$ARJUN_INSTALLED" == false ]]; then
                if pip3 install arjun &> /dev/null; then
                    ARJUN_INSTALLED=true
                    echo -e "${GREEN}✅ Arjun installed via pip3${NC}"
                fi
            fi
            ;;
            
        "debian")
            # Method 1: pipx (recommended for Debian/Ubuntu/Parrot OS)
            if command -v pipx &> /dev/null; then
                if pipx install arjun &> /dev/null; then
                    ARJUN_INSTALLED=true
                    echo -e "${GREEN}✅ Arjun installed via pipx${NC}"
                fi
            fi
            
            # Method 2: pip3 with appropriate flags
            if [[ "$ARJUN_INSTALLED" == false ]]; then
                if pip3 install --break-system-packages arjun &> /dev/null; then
                    ARJUN_INSTALLED=true
                    echo -e "${GREEN}✅ Arjun installed via pip3 (system packages)${NC}"
                elif pip3 install arjun &> /dev/null; then
                    ARJUN_INSTALLED=true
                    echo -e "${GREEN}✅ Arjun installed via pip3${NC}"
                fi
            fi
            ;;
            
        *)
            # Generic installation for other systems
            if command -v pipx &> /dev/null; then
                if pipx install arjun &> /dev/null; then
                    ARJUN_INSTALLED=true
                    echo -e "${GREEN}✅ Arjun installed via pipx${NC}"
                fi
            elif pip3 install arjun &> /dev/null; then
                ARJUN_INSTALLED=true
                echo -e "${GREEN}✅ Arjun installed via pip3${NC}"
            fi
            ;;
    esac
    
    # Universal fallback: user installation
    if [[ "$ARJUN_INSTALLED" == false ]]; then
        if python3 -m pip install --user arjun &> /dev/null; then
            ARJUN_INSTALLED=true
            echo -e "${GREEN}✅ Arjun installed via python3 -m pip (user)${NC}"
            [[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"
        fi
    fi
    
    if [[ "$ARJUN_INSTALLED" == false ]]; then
        echo -e "${RED}❌ Arjun installation failed${NC}"
    fi
else
    echo -e "${GREEN}✅ Arjun already installed${NC}"
fi

# Install ParamSpider (required tool)
if ! command -v paramspider &> /dev/null; then
    echo -e "${BLUE}🔄 Installing ParamSpider...${NC}"
    
    PARAMSPIDER_INSTALLED=false
    
    # Method 1: pipx (recommended for tool isolation)
    if command -v pipx &> /dev/null; then
        if pipx install git+https://github.com/devanshbatham/ParamSpider.git &> /dev/null; then
            PARAMSPIDER_INSTALLED=true
            echo -e "${GREEN}✅ ParamSpider installed via pipx${NC}"
        fi
    fi
    
    # Method 2: Modern pip install approach
    if [[ "$PARAMSPIDER_INSTALLED" == false ]]; then
        if [[ -d "/tmp/ParamSpider" ]]; then
            rm -rf /tmp/ParamSpider
        fi
        
        if git clone https://github.com/devanshbatham/ParamSpider.git /tmp/ParamSpider &> /dev/null; then
            cd /tmp/ParamSpider
            
            # Try multiple pip installation methods (modern approach)
            if pip3 install --break-system-packages . &> /dev/null; then
                PARAMSPIDER_INSTALLED=true
                echo -e "${GREEN}✅ ParamSpider installed via pip3 (system packages)${NC}"
            elif pip3 install . &> /dev/null; then
                PARAMSPIDER_INSTALLED=true
                echo -e "${GREEN}✅ ParamSpider installed via pip3${NC}"
            elif python3 -m pip install --user . &> /dev/null; then
                PARAMSPIDER_INSTALLED=true
                echo -e "${GREEN}✅ ParamSpider installed via python3 -m pip (user)${NC}"
                export PATH="$HOME/.local/bin:$PATH"
            elif python3 -m pip install . &> /dev/null; then
                PARAMSPIDER_INSTALLED=true
                echo -e "${GREEN}✅ ParamSpider installed via python3 -m pip${NC}"
            fi
            
            cd - > /dev/null
        fi
    fi
    
    if [[ "$PARAMSPIDER_INSTALLED" == false ]]; then
        echo -e "${RED}❌ ParamSpider installation failed${NC}"
    fi
else
    echo -e "${GREEN}✅ ParamSpider already installed${NC}"
    # Quick verification that it's working
    if ! paramspider --help &> /dev/null; then
        echo -e "${YELLOW}⚠️  ParamSpider command exists but appears broken - reinstalling...${NC}"
        # Clean reinstallation
        if command -v pipx &> /dev/null; then
            pipx uninstall paramspider &> /dev/null || true
            if pipx install git+https://github.com/devanshbatham/ParamSpider.git &> /dev/null; then
                echo -e "${GREEN}✅ ParamSpider reinstalled via pipx${NC}"
            fi
        fi
    fi
fi

# Install CMSeek (required tool)
if ! command -v cmseek &> /dev/null; then
    echo -e "${BLUE}🔄 Installing CMSeek...${NC}"
    if [[ -d "/tmp/CMSeek" ]]; then
        rm -rf /tmp/CMSeek
    fi
    
    if git clone https://github.com/Tuhinshubhra/CMSeek.git /tmp/CMSeek &> /dev/null; then
        cd /tmp/CMSeek
        if (pip3 install --break-system-packages -r requirements.txt &> /dev/null || pip3 install -r requirements.txt &> /dev/null || python3 -m pip install --user -r requirements.txt &> /dev/null) && \
           sudo ln -sf "$(pwd)/cmseek.py" /usr/local/bin/cmseek 2>/dev/null && \
           sudo chmod +x /usr/local/bin/cmseek 2>/dev/null; then
            echo -e "${GREEN}✅ CMSeek installed${NC}"
        else
            echo -e "${RED}❌ CMSeek installation failed${NC}"
        fi
        cd - > /dev/null
    else
        echo -e "${RED}❌ CMSeek download failed${NC}"
    fi
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
                # Install from GitHub source (CeWL is not available as a gem)
                echo -e "${BLUE}🔄 Installing CeWL from GitHub source...${NC}"
                if [[ -d "/tmp/CeWL" ]]; then
                    rm -rf /tmp/CeWL
                fi
                
                if git clone https://github.com/digininja/CeWL.git /tmp/CeWL &> /dev/null; then
                    cd /tmp/CeWL
                    
                    # Install required gems with fallback for older Ruby versions
                    GEMS_INSTALLED=false
                    if gem install --user-install mime mime-types rubyzip spider rexml &> /dev/null; then
                        # Try to install nokogiri (may need older version for older Ruby)
                        if gem install --user-install nokogiri &> /dev/null || gem install --user-install nokogiri -v 1.13.10 &> /dev/null; then
                            # Try to install mini_exiftool
                            if gem install --user-install mini_exiftool &> /dev/null; then
                                GEMS_INSTALLED=true
                            fi
                        fi
                    fi
                    
                    if [[ "$GEMS_INSTALLED" == true ]]; then
                        # Move to permanent location
                        sudo mv /tmp/CeWL /opt/CeWL 2>/dev/null || sudo cp -r /tmp/CeWL /opt/CeWL
                        
                        # Create wrapper script that handles gem paths
                        cat << 'WRAPPER_EOF' | sudo tee /usr/local/bin/cewl > /dev/null
#!/bin/bash
# CeWL wrapper script
export PATH="$HOME/.gem/ruby/*/bin:/usr/local/bin:$PATH"
exec ruby /opt/CeWL/cewl.rb "$@"
WRAPPER_EOF
                        sudo chmod +x /usr/local/bin/cewl
                        echo -e "${GREEN}✅ CeWL installed from GitHub${NC}"
                    else
                        echo -e "${YELLOW}⚠️  CeWL dependencies installation failed${NC}"
                    fi
                    cd - > /dev/null
                else
                    echo -e "${YELLOW}⚠️  CeWL download failed${NC}"
                    echo -e "${CYAN}💡 You can still use ipsnipe - CeWL provides custom wordlist generation${NC}"
                fi
            fi
            ;;
        "macos"|"arch")
            # Install from GitHub source (CeWL is not available as a gem)
            echo -e "${BLUE}🔄 Installing CeWL from GitHub source...${NC}"
            if [[ -d "/tmp/CeWL" ]]; then
                rm -rf /tmp/CeWL
            fi
            
            if git clone https://github.com/digininja/CeWL.git /tmp/CeWL &> /dev/null; then
                cd /tmp/CeWL
                
                # Install required gems with fallback for older Ruby versions
                GEMS_INSTALLED=false
                if gem install --user-install mime mime-types rubyzip spider rexml &> /dev/null; then
                    # Try to install nokogiri (may need older version for older Ruby)
                    if gem install --user-install nokogiri &> /dev/null || gem install --user-install nokogiri -v 1.13.10 &> /dev/null; then
                        # Try to install mini_exiftool
                        if gem install --user-install mini_exiftool &> /dev/null; then
                            GEMS_INSTALLED=true
                        fi
                    fi
                fi
                
                if [[ "$GEMS_INSTALLED" == true ]]; then
                    # Move to permanent location
                    sudo mv /tmp/CeWL /opt/CeWL 2>/dev/null || sudo cp -r /tmp/CeWL /opt/CeWL
                    
                    # Create wrapper script that handles gem paths
                    cat << 'WRAPPER_EOF' | sudo tee /usr/local/bin/cewl > /dev/null
#!/bin/bash
# CeWL wrapper script
export PATH="$HOME/.gem/ruby/*/bin:/usr/local/bin:$PATH"
exec ruby /opt/CeWL/cewl.rb "$@"
WRAPPER_EOF
                    sudo chmod +x /usr/local/bin/cewl
                    echo -e "${GREEN}✅ CeWL installed from GitHub${NC}"
                else
                    echo -e "${YELLOW}⚠️  CeWL dependencies installation failed${NC}"
                fi
                cd - > /dev/null
            else
                echo -e "${YELLOW}⚠️  CeWL download failed${NC}"
                echo -e "${CYAN}💡 You can still use ipsnipe - CeWL provides custom wordlist generation${NC}"
            fi
            ;;
    esac
fi

# Install theHarvester (required OSINT tool)
if ! command -v theHarvester &> /dev/null; then
    echo -e "${BLUE}🔄 Installing theHarvester...${NC}"
    if [[ -d "/tmp/theHarvester" ]]; then
        rm -rf /tmp/theHarvester
    fi
    
    if git clone https://github.com/laramies/theHarvester.git /tmp/theHarvester &> /dev/null; then
        cd /tmp/theHarvester
        if (pip3 install --break-system-packages -r requirements.txt &> /dev/null || pip3 install -r requirements.txt &> /dev/null || python3 -m pip install --user -r requirements.txt &> /dev/null) && \
           sudo ln -sf "$(pwd)/theHarvester.py" /usr/local/bin/theHarvester 2>/dev/null && \
           sudo chmod +x /usr/local/bin/theHarvester 2>/dev/null; then
            echo -e "${GREEN}✅ theHarvester installed${NC}"
        else
            echo -e "${RED}❌ theHarvester installation failed${NC}"
        fi
        cd - > /dev/null
    else
        echo -e "${RED}❌ theHarvester download failed${NC}"
    fi
fi

# Install WhatWeb (web technology detection)
if ! command -v whatweb &> /dev/null; then
    echo -e "${BLUE}🔄 Installing WhatWeb...${NC}"
    
    case $OS in
        "debian")
            # Try apt first, then manual installation
            if sudo apt install -y whatweb &> /dev/null; then
                echo -e "${GREEN}✅ WhatWeb installed${NC}"
            elif git clone https://github.com/urbanadventurer/WhatWeb.git /tmp/WhatWeb &> /dev/null && \
                 sudo cp /tmp/WhatWeb/whatweb /usr/local/bin/ 2>/dev/null && \
                 sudo chmod +x /usr/local/bin/whatweb 2>/dev/null; then
                echo -e "${GREEN}✅ WhatWeb installed${NC}"
            else
                echo -e "${RED}❌ WhatWeb installation failed${NC}"
            fi
            ;;
        "macos")
            # Try manual installation for macOS
            if [[ -d "/tmp/WhatWeb" ]]; then
                rm -rf /tmp/WhatWeb
            fi
            if git clone https://github.com/urbanadventurer/WhatWeb.git /tmp/WhatWeb &> /dev/null && \
               sudo cp /tmp/WhatWeb/whatweb /usr/local/bin/ 2>/dev/null && \
               sudo chmod +x /usr/local/bin/whatweb 2>/dev/null; then
                echo -e "${GREEN}✅ WhatWeb installed${NC}"
            else
                echo -e "${RED}❌ WhatWeb installation failed${NC}"
            fi
            ;;
        "arch")
            if sudo pacman -S --noconfirm whatweb &> /dev/null; then
                echo -e "${GREEN}✅ WhatWeb installed${NC}"
            else
                echo -e "${RED}❌ WhatWeb installation failed${NC}"
            fi
            ;;
    esac
fi

# Install advanced HTB tools for enhanced DNS enumeration
echo -e "\n${YELLOW}🚀 Installing HTB-optimized advanced tools...${NC}"

# Install Subfinder (advanced subdomain enumeration)
if ! command -v subfinder &> /dev/null; then
    echo -e "${BLUE}🔄 Installing Subfinder...${NC}"
    
    # Check if Go is installed (preferred method)
    if command -v go &> /dev/null; then
        if go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest &> /dev/null; then
            # Ensure Go bin is in PATH and create system symlink
            if [[ -f "$HOME/go/bin/subfinder" ]]; then
                sudo ln -sf "$HOME/go/bin/subfinder" /usr/local/bin/subfinder 2>/dev/null
                echo -e "${GREEN}✅ Subfinder installed${NC}"
            else
                echo -e "${RED}❌ Subfinder installation failed${NC}"
            fi
        else
            echo -e "${RED}❌ Subfinder Go installation failed${NC}"
        fi
    else
                    # Try Homebrew on macOS
            if [[ "$OS" == "macos" ]] && command -v brew &> /dev/null; then
                if brew install subfinder &> /dev/null; then
                echo -e "${GREEN}✅ Subfinder installed${NC}"
            else
                echo -e "${RED}❌ Subfinder Homebrew installation failed${NC}"
            fi
        else
            echo -e "${RED}❌ Subfinder installation failed - Go or Homebrew required${NC}"
        fi
    fi
fi

# Install Amass (advanced OSINT tool)
if ! command -v amass &> /dev/null; then
    echo -e "${BLUE}🔄 Installing Amass...${NC}"
    
    case $OS in
        "debian")
            # Try installing via snap first (most reliable)
            if command -v snap &> /dev/null && sudo snap install amass &> /dev/null; then
                echo -e "${GREEN}✅ Amass installed${NC}"
            else
                echo -e "${RED}❌ Amass snap installation failed${NC}"
            fi
            ;;
        "macos")
            # Use Homebrew
            if command -v brew &> /dev/null && brew install amass &> /dev/null; then
                echo -e "${GREEN}✅ Amass installed${NC}"
            else
                echo -e "${RED}❌ Amass Homebrew installation failed${NC}"
            fi
            ;;
        "arch")
            # Try AUR installation
            if command -v yay &> /dev/null && yay -S amass --noconfirm &> /dev/null; then
                echo -e "${GREEN}✅ Amass installed${NC}"
            else
                echo -e "${RED}❌ Amass AUR installation failed${NC}"
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

# Refresh PATH to ensure newly installed tools are found
echo -e "\n${BLUE}🔄 Refreshing PATH for verification...${NC}"
# Re-export all potential tool paths (OS-agnostic)
[[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"
[[ -d "$HOME/go/bin" ]] && export PATH="$HOME/go/bin:$PATH"
case "$OSTYPE" in
    "darwin"*)
        # Auto-detect Homebrew installation paths
        for brew_path in "/opt/homebrew" "/usr/local"; do
            [[ -d "$brew_path/bin" ]] && export PATH="$brew_path/bin:$PATH"
        done
        ;;
    "linux-gnu"*)
        [[ -d "/usr/local/bin" ]] && export PATH="/usr/local/bin:$PATH"
        [[ -d "/usr/bin" ]] && export PATH="/usr/bin:$PATH"
        ;;
esac

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
    
    # Simple verification without debug messages
    if command -v "$command_name" &> /dev/null; then
        echo -e "${GREEN}✅ $tool_name found${NC}"
    else
        echo -e "${YELLOW}⚠️  $tool_name not found (optional)${NC}"
    fi
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

# Note: HTB environments typically provide wordlists
echo -e "${BLUE}ℹ️  HTB environments provide comprehensive wordlists${NC}"

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
    echo -e "${BLUE}   • HTB-optimized wordlist support (uses environment wordlists)${NC}"
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
echo -e "${BLUE}• HTB environments provide comprehensive wordlists for reconnaissance${NC}"

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

# Wait for user to press Enter before closing
echo -e "\n${YELLOW}Press Enter to close the terminal...${NC}"
read -r