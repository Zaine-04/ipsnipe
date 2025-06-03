#!/bin/bash

# ipsnipe Uninstall Script (Shell Version)
# This script will help you remove ipsnipe and its dependencies safely.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ipsnipe Banner
print_banner() {
    echo -e "${RED}"
    cat << "EOF"
 ___  ________  ________  ________   ___  ________  _______      
|\  \|\   __  \|\   ____\|\   ___  \|\  \|\   __  \|\  ___ \     
\ \  \ \  \|\  \ \  \___|\ \  \\ \  \ \  \ \  \|\  \ \   __/|    
 \ \  \ \   ____\ \_____  \ \  \\ \  \ \  \ \   ____\ \  \_|/__  
  \ \  \ \  \___|\|____|\  \ \  \\ \  \ \  \ \  \___|\ \  \_|\ \ 
   \ \__\ \__\     ____\_\  \ \__\\ \__\ \__\ \__\    \ \_______\
    \|__|\|__|    |\_________\|__| \|__|\|__|\|__|     \|_______|
                  \|_________|                                   

        🗑️  ipsnipe Uninstall Script 🗑️
        ═══════════════════════════════════
EOF
    echo -e "${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            echo "debian"
        elif command -v pacman &> /dev/null; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Check if a command exists
check_command() {
    local cmd="$1"
    
    # Method 1: command -v (most reliable in shell)
    if command -v "$cmd" &> /dev/null; then
        return 0
    fi
    
    # Method 2: which command
    if which "$cmd" &> /dev/null; then
        return 0
    fi
    
    # Method 3: direct path check for common locations
            # Check common installation paths (auto-detect Homebrew)
        SEARCH_PATHS=("/usr/local/bin/$cmd" "/usr/bin/$cmd" "$HOME/go/bin/$cmd")
        
        # Add Homebrew paths dynamically
        for brew_path in "/opt/homebrew" "/usr/local"; do
            [[ -d "$brew_path/bin" ]] && SEARCH_PATHS+=("$brew_path/bin/$cmd")
        done
        
        for path in "${SEARCH_PATHS[@]}"; do
        if [[ -x "$path" ]]; then
            return 0
        fi
    done
    
    return 1
}

# Check if a Python package is installed
check_python_package() {
    local package="$1"
    
    # Method 1: Direct import test
    if python3 -c "import $package" &> /dev/null; then
        return 0
    fi
    
    # Method 2: pip show check
    if python3 -m pip show "$package" &> /dev/null; then
        return 0
    fi
    
    # Method 3: pip list check
    if python3 -m pip list 2>/dev/null | grep -i "^$package " &> /dev/null; then
        return 0
    fi
    
    return 1
}

# Scan for installed dependencies
scan_dependencies() {
    echo -e "${YELLOW}🔍 Scanning for installed dependencies...${NC}\n"
    
    # Python packages (updated)
    echo -e "${CYAN}🐍 Python Packages:${NC}"
    PYTHON_PACKAGES=("toml" "rich" "requests")
    INSTALLED_PYTHON=()
    
    for package in "${PYTHON_PACKAGES[@]}"; do
        if check_python_package "$package"; then
            INSTALLED_PYTHON+=("$package")
            echo -e "${GREEN}✅ $package - INSTALLED${NC}"
        else
            echo -e "${YELLOW}⚪ $package - not installed${NC}"
        fi
    done
    
    # System tools (updated)
    echo -e "\n${CYAN}🛠️  System Tools:${NC}"
    SYSTEM_TOOLS=("nmap" "feroxbuster" "ffuf" "theHarvester" "whatweb" "ruby" "cewl" "curl" "dig" "host" "whois" "waybackurls" "subfinder" "assetfinder" "amass" "dnsrecon" "rustscan" "gobuster" "dirb" "nuclei" "httpx" "katana" "paramspider")
    INSTALLED_TOOLS=()
    
    for tool in "${SYSTEM_TOOLS[@]}"; do
        if check_command "$tool"; then
            INSTALLED_TOOLS+=("$tool")
            echo -e "${GREEN}✅ $tool - INSTALLED${NC}"
        else
            echo -e "${YELLOW}⚪ $tool - not installed${NC}"
        fi
    done
    
    # Project files and directories (updated)
    echo -e "\n${CYAN}📁 Project Files & Directories:${NC}"
    PROJECT_ITEMS=(
        # Main files
        "ipsnipe.py" "requirements.txt" "install.sh" "config.toml" "README.md" "LICENSE" 
        "CHANGELOG.md" "uninstall.py" "uninstall.sh" ".gitignore" "UI_IMPROVEMENT_SUMMARY.md"
        # Main directories
        "ipsnipe/" "legacy_file/" "misc/" "__pycache__/" ".git/" ".vscode/"
        # Python cache directories
        "ipsnipe/__pycache__/" "ipsnipe/ui/__pycache__/" "ipsnipe/scanners/__pycache__/"
        "ipsnipe/core/__pycache__/" "legacy_file/__pycache__/"
        # macOS files
        ".DS_Store"
    )
    FOUND_FILES=()
    
    for item in "${PROJECT_ITEMS[@]}"; do
        if [[ -e "$item" ]]; then
            FOUND_FILES+=("$item")
            if [[ -d "$item" ]]; then
                echo -e "${GREEN}✅ $item (directory) - FOUND${NC}"
            else
                echo -e "${GREEN}✅ $item - FOUND${NC}"
            fi
        fi
    done
    
    # Check for scan result directories (ipsnipe_scan_*)
    for scan_dir in ipsnipe_scan_*; do
        if [[ -d "$scan_dir" ]]; then
            FOUND_FILES+=("$scan_dir")
            echo -e "${GREEN}✅ $scan_dir (scan results) - FOUND${NC}"
        fi
    done
    
    # System binaries (updated)
    SYSTEM_BINARIES=(
        "/usr/local/bin/theHarvester" "/usr/local/bin/whatweb" "/usr/local/bin/feroxbuster"
        "/usr/local/bin/ffuf" "/usr/local/bin/gobuster" "/usr/local/bin/nuclei"
        "/usr/local/bin/httpx" "/usr/local/bin/katana" "/usr/local/bin/waybackurls"
        "/usr/local/bin/subfinder" "/usr/local/bin/assetfinder" "/usr/local/bin/amass"
        "/usr/local/bin/rustscan" "/usr/local/bin/paramspider"
    )
    for binary in "${SYSTEM_BINARIES[@]}"; do
        if [[ -e "$binary" ]]; then
            FOUND_FILES+=("$binary")
            echo -e "${GREEN}✅ $binary - FOUND${NC}"
        fi
    done
}

# Confirm what will be uninstalled
confirm_uninstall() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📋 Uninstall Summary${NC}\n"
    
    if [[ ${#INSTALLED_PYTHON[@]} -eq 0 && ${#INSTALLED_TOOLS[@]} -eq 0 && ${#FOUND_FILES[@]} -eq 0 ]]; then
        echo -e "${GREEN}✨ No ipsnipe dependencies found to uninstall!${NC}"
        return 1
    fi
    
    if [[ ${#INSTALLED_PYTHON[@]} -gt 0 ]]; then
        echo -e "${RED}🐍 Python packages to be REMOVED:${NC}"
        for package in "${INSTALLED_PYTHON[@]}"; do
            echo -e "   • $package"
        done
    fi
    
    if [[ ${#INSTALLED_TOOLS[@]} -gt 0 ]]; then
        echo -e "\n${RED}🛠️  System tools to be REMOVED:${NC}"
        for tool in "${INSTALLED_TOOLS[@]}"; do
            echo -e "   • $tool"
        done
    fi
    
    if [[ ${#FOUND_FILES[@]} -gt 0 ]]; then
        echo -e "\n${RED}📁 Project files to be REMOVED:${NC}"
        for file in "${FOUND_FILES[@]}"; do
            echo -e "   • $file"
        done
    fi
    
    echo -e "\n${YELLOW}⚠️  WARNING: This will remove the above dependencies and files.${NC}"
    echo -e "${YELLOW}Some tools might be used by other applications!${NC}"
    
    return 0
}

# Ask about selective removal
ask_selective_removal() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🤔 Do you want to keep any of these dependencies?${NC}"
    
    KEEP_PYTHON=()
    KEEP_TOOLS=()
    
    # Ask about Python packages
    if [[ ${#INSTALLED_PYTHON[@]} -gt 0 ]]; then
        echo -e "\n${YELLOW}Keep Python packages? (y/N): ${NC}"
        read -r RESPONSE
        if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
            echo -e "\n${BLUE}Select Python packages to KEEP:${NC}"
            for i in "${!INSTALLED_PYTHON[@]}"; do
                echo -e "   $((i+1)). ${INSTALLED_PYTHON[i]}"
            done
            
            echo -e "\n${YELLOW}Enter package numbers to keep (space-separated, or 'none'): ${NC}"
            read -r CHOICES
            
            if [[ "$CHOICES" != "none" ]]; then
                for choice in $CHOICES; do
                    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -gt 0 ]] && [[ $choice -le ${#INSTALLED_PYTHON[@]} ]]; then
                        idx=$((choice-1))
                        KEEP_PYTHON+=("${INSTALLED_PYTHON[idx]}")
                        echo -e "${GREEN}✅ Will keep: ${INSTALLED_PYTHON[idx]}${NC}"
                    fi
                done
            fi
        fi
    fi
    
    # Ask about system tools
    if [[ ${#INSTALLED_TOOLS[@]} -gt 0 ]]; then
        echo -e "\n${YELLOW}Keep system tools? (y/N): ${NC}"
        read -r RESPONSE
        if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
            echo -e "\n${BLUE}Select system tools to KEEP:${NC}"
            for i in "${!INSTALLED_TOOLS[@]}"; do
                echo -e "   $((i+1)). ${INSTALLED_TOOLS[i]}"
            done
            
            echo -e "\n${YELLOW}Enter tool numbers to keep (space-separated, or 'none'): ${NC}"
            read -r CHOICES
            
            if [[ "$CHOICES" != "none" ]]; then
                for choice in $CHOICES; do
                    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -gt 0 ]] && [[ $choice -le ${#INSTALLED_TOOLS[@]} ]]; then
                        idx=$((choice-1))
                        KEEP_TOOLS+=("${INSTALLED_TOOLS[idx]}")
                        echo -e "${GREEN}✅ Will keep: ${INSTALLED_TOOLS[idx]}${NC}"
                    fi
                done
            fi
        fi
    fi
}

# Final confirmation
final_confirmation() {
    # Calculate what will be removed
    REMOVE_PYTHON=()
    for package in "${INSTALLED_PYTHON[@]}"; do
        if [[ ! " ${KEEP_PYTHON[@]} " =~ " ${package} " ]]; then
            REMOVE_PYTHON+=("$package")
        fi
    done
    
    REMOVE_TOOLS=()
    for tool in "${INSTALLED_TOOLS[@]}"; do
        if [[ ! " ${KEEP_TOOLS[@]} " =~ " ${tool} " ]]; then
            REMOVE_TOOLS+=("$tool")
        fi
    done
    
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📋 Final Uninstall Plan${NC}\n"
    
    if [[ ${#REMOVE_PYTHON[@]} -gt 0 ]]; then
        echo -e "${RED}🐍 Python packages to REMOVE:${NC}"
        for package in "${REMOVE_PYTHON[@]}"; do
            echo -e "   • $package"
        done
    fi
    
    if [[ ${#REMOVE_TOOLS[@]} -gt 0 ]]; then
        echo -e "\n${RED}🛠️  System tools to REMOVE:${NC}"
        for tool in "${REMOVE_TOOLS[@]}"; do
            echo -e "   • $tool"
        done
    fi
    
    if [[ ${#FOUND_FILES[@]} -gt 0 ]]; then
        echo -e "\n${RED}📁 Project files to REMOVE:${NC}"
        for file in "${FOUND_FILES[@]}"; do
            echo -e "   • $file"
        done
    fi
    
    if [[ ${#KEEP_PYTHON[@]} -gt 0 ]]; then
        echo -e "\n${GREEN}🐍 Python packages to KEEP:${NC}"
        for package in "${KEEP_PYTHON[@]}"; do
            echo -e "   • $package"
        done
    fi
    
    if [[ ${#KEEP_TOOLS[@]} -gt 0 ]]; then
        echo -e "\n${GREEN}🛠️  System tools to KEEP:${NC}"
        for tool in "${KEEP_TOOLS[@]}"; do
            echo -e "   • $tool"
        done
    fi
    
    if [[ ${#REMOVE_PYTHON[@]} -eq 0 && ${#REMOVE_TOOLS[@]} -eq 0 && ${#FOUND_FILES[@]} -eq 0 ]]; then
        echo -e "${GREEN}✨ Nothing to uninstall!${NC}"
        return 1
    fi
    
    echo -e "\n${RED}⚠️  WARNING: This action cannot be undone!${NC}"
    echo -e "${YELLOW}Proceed with uninstall? (y/N): ${NC}"
    read -r RESPONSE
    [[ "$RESPONSE" =~ ^[Yy]$ ]]
}

# Uninstall Python packages
uninstall_python_packages() {
    REMOVE_PYTHON=()
    for package in "${INSTALLED_PYTHON[@]}"; do
        if [[ ! " ${KEEP_PYTHON[@]} " =~ " ${package} " ]]; then
            REMOVE_PYTHON+=("$package")
        fi
    done
    
    if [[ ${#REMOVE_PYTHON[@]} -eq 0 ]]; then
        return
    fi
    
    echo -e "\n${YELLOW}🐍 Uninstalling Python packages...${NC}"
    for package in "${REMOVE_PYTHON[@]}"; do
        echo -e "   Removing $package..."
        if python3 -m pip uninstall -y "$package" &> /dev/null; then
            echo -e "${GREEN}✅ $package removed successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  $package - may not have been installed via pip${NC}"
        fi
    done
}

# Uninstall system tools
uninstall_system_tools() {
    REMOVE_TOOLS=()
    for tool in "${INSTALLED_TOOLS[@]}"; do
        if [[ ! " ${KEEP_TOOLS[@]} " =~ " ${tool} " ]]; then
            REMOVE_TOOLS+=("$tool")
        fi
    done
    
    if [[ ${#REMOVE_TOOLS[@]} -eq 0 ]]; then
        return
    fi
    
    echo -e "\n${YELLOW}🛠️  Uninstalling system tools...${NC}"
    
    OS=$(detect_os)
    
    case $OS in
        "debian")
            APT_TOOLS=()
            for tool in "${REMOVE_TOOLS[@]}"; do
                if [[ "$tool" =~ ^(nmap|ruby|whatweb|curl|dig|host|whois|gobuster|dirb|dnsrecon)$ ]]; then
                    APT_TOOLS+=("$tool")
                fi
            done
            
            if [[ ${#APT_TOOLS[@]} -gt 0 ]]; then
                echo -e "   Removing via apt: ${APT_TOOLS[*]}"
                if sudo apt remove -y "${APT_TOOLS[@]}" &> /dev/null; then
                    echo -e "${GREEN}✅ APT packages removed${NC}"
                else
                    echo -e "${RED}❌ Failed to remove some APT packages${NC}"
                fi
            fi
            ;;
            
        "macos")
            if command -v brew &> /dev/null; then
                BREW_TOOLS=()
                for tool in "${REMOVE_TOOLS[@]}"; do
                    if [[ "$tool" =~ ^(nmap|feroxbuster|ffuf|ruby|cewl|curl|dig|whois|waybackurls|subfinder|assetfinder|amass|gobuster|nuclei|httpx|katana)$ ]]; then
                        BREW_TOOLS+=("$tool")
                    fi
                done
                
                if [[ ${#BREW_TOOLS[@]} -gt 0 ]]; then
                    echo -e "   Removing via brew: ${BREW_TOOLS[*]}"
                    if brew uninstall "${BREW_TOOLS[@]}" &> /dev/null; then
                        echo -e "${GREEN}✅ Homebrew packages removed${NC}"
                    else
                        echo -e "${RED}❌ Failed to remove some Homebrew packages${NC}"
                    fi
                fi
            fi
            ;;
            
        "arch")
            PACMAN_TOOLS=()
            for tool in "${REMOVE_TOOLS[@]}"; do
                if [[ "$tool" =~ ^(nmap|ruby|feroxbuster|ffuf|whatweb|curl|dig|whois|gobuster|dirb)$ ]]; then
                    PACMAN_TOOLS+=("$tool")
                fi
            done
            
            if [[ ${#PACMAN_TOOLS[@]} -gt 0 ]]; then
                echo -e "   Removing via pacman: ${PACMAN_TOOLS[*]}"
                if sudo pacman -R --noconfirm "${PACMAN_TOOLS[@]}" &> /dev/null; then
                    echo -e "${GREEN}✅ Pacman packages removed${NC}"
                else
                    echo -e "${RED}❌ Failed to remove some pacman packages${NC}"
                fi
            fi
            ;;
    esac
    
    # Remove manually installed tools and Go-based tools
    MANUAL_TOOLS=("theHarvester" "waybackurls" "subfinder" "assetfinder" "amass" "rustscan" "nuclei" "httpx" "katana" "paramspider")
    for tool in "${REMOVE_TOOLS[@]}"; do
        if [[ " ${MANUAL_TOOLS[@]} " =~ " ${tool} " ]]; then
            case $tool in
                "theHarvester")
                    for path in "/usr/local/bin/theHarvester" "/usr/bin/theHarvester"; do
                        if [[ -f "$path" ]]; then
                            sudo rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "waybackurls")
                    for path in "/usr/local/bin/waybackurls" "/usr/bin/waybackurls" "$HOME/go/bin/waybackurls"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "subfinder")
                    for path in "/usr/local/bin/subfinder" "/usr/bin/subfinder" "$HOME/go/bin/subfinder"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "assetfinder")
                    for path in "/usr/local/bin/assetfinder" "/usr/bin/assetfinder" "$HOME/go/bin/assetfinder"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "amass")
                    for path in "/usr/local/bin/amass" "/usr/bin/amass" "$HOME/go/bin/amass"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "rustscan")
                    for path in "/usr/local/bin/rustscan" "/usr/bin/rustscan"; do
                        if [[ -f "$path" ]]; then
                            sudo rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "nuclei")
                    for path in "/usr/local/bin/nuclei" "/usr/bin/nuclei" "$HOME/go/bin/nuclei"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "httpx")
                    for path in "/usr/local/bin/httpx" "/usr/bin/httpx" "$HOME/go/bin/httpx"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "katana")
                    for path in "/usr/local/bin/katana" "/usr/bin/katana" "$HOME/go/bin/katana"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
                "paramspider")
                    for path in "/usr/local/bin/paramspider" "/usr/bin/paramspider"; do
                        if [[ -f "$path" ]]; then
                            rm -f "$path"
                            echo -e "${GREEN}✅ Removed $path${NC}"
                        fi
                    done
                    ;;
            esac
        fi
    done
}

# Remove project files
remove_project_files() {
    if [[ ${#FOUND_FILES[@]} -eq 0 ]]; then
        return
    fi
    
    echo -e "\n${YELLOW}📁 Removing project files...${NC}"
    for file in "${FOUND_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            rm -f "$file"
            echo -e "${GREEN}✅ Removed file: $file${NC}"
        elif [[ -d "$file" ]]; then
            rm -rf "$file"
            echo -e "${GREEN}✅ Removed directory: $file${NC}"
        fi
    done
}

# Main function
main() {
    print_banner
    
    echo -e "${BLUE}This script will help you safely remove ipsnipe and its dependencies.${NC}"
    echo -e "${YELLOW}⚠️  Note: Some tools may be used by other applications!${NC}\n"
    
    # Scan for dependencies
    scan_dependencies
    
    # Confirm what will be uninstalled
    if ! confirm_uninstall; then
        echo -e "\n${GREEN}✨ Uninstall complete - nothing to remove!${NC}"
        exit 0
    fi
    
    # Ask about selective removal
    ask_selective_removal
    
    # Final confirmation
    if ! final_confirmation; then
        echo -e "\n${BLUE}💡 Uninstall cancelled.${NC}"
        exit 0
    fi
    
    # Perform uninstall
    echo -e "\n${GREEN}🚀 Starting uninstall process...${NC}"
    
    uninstall_python_packages
    uninstall_system_tools
    remove_project_files
    
    echo -e "\n${GREEN}✅ Uninstall completed successfully!${NC}"
    echo -e "${BLUE}Thank you for using ipsnipe! 🚀${NC}"
}

# Handle Ctrl+C
trap 'echo -e "\n${YELLOW}⚠️  Uninstall cancelled by user${NC}"; exit 1' INT

# Run main function
main "$@" 