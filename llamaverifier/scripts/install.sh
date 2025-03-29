#!/bin/bash
#
# LlamaVerifier Master Installer Script
# A comprehensive installation and setup script for LlamaVerifier
# Zero-Knowledge Proof System for AI Model Verification
# ------------------------------------------------------------

# Color codes for UI
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Unicode symbols
CHECK_MARK="\xE2\x9C\x94"
CROSS_MARK="\xE2\x9C\x96"
LLAMA="\xF0\x9F\xA6\x99"

# Default installation directory
DEFAULT_INSTALL_DIR="$HOME/.llamaverifier"
INSTALL_DIR="$DEFAULT_INSTALL_DIR"

# Repository URL
REPO_URL="https://github.com/username/llamaverifier.git"

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

# Print banner
print_banner() {
    echo -e "${PURPLE}"
    echo "  _      _                       _   _           _  __ _           "
    echo " | |    | |                     | | | |         (_)/ _(_)          "
    echo " | |    | | __ _ _ __ ___   __ _| | | | ___ _ __ _| |_ _  ___ _ __ "
    echo " | |    | |/ _\` | '_ \` _ \ / _\` | | | |/ _ \ '__| |  _| |/ _ \ '__|"
    echo " | |____| | (_| | | | | | | (_| | | | |  __/ |  | | | | |  __/ |   "
    echo " |______|_|\__,_|_| |_| |_|\__,_|_| |_|\___|_|  |_|_| |_|\___|_|   "
    echo "                                                                   "
    echo -e "${NC}"
    echo -e "${CYAN}Zero-Knowledge Proof System for AI Model Verification${NC}"
    echo -e "${YELLOW}Apple Silicon Optimized | MLX Accelerated${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    echo -e "${BLUE}${BOLD}Checking system requirements...${NC}"
    
    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            echo -e "  ${GREEN}${CHECK_MARK} Python $PYTHON_VERSION${NC}"
        else
            echo -e "  ${RED}${CROSS_MARK} Python $PYTHON_VERSION (required: >= 3.8)${NC}"
            echo -e "  ${YELLOW}Please install Python 3.8 or higher${NC}"
            exit 1
        fi
    else
        echo -e "  ${RED}${CROSS_MARK} Python not found${NC}"
        echo -e "  ${YELLOW}Please install Python 3.8 or higher${NC}"
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        echo -e "  ${GREEN}${CHECK_MARK} pip3${NC}"
    else
        echo -e "  ${RED}${CROSS_MARK} pip3 not found${NC}"
        echo -e "  ${YELLOW}Please install pip3${NC}"
        exit 1
    fi
    
    # Check git
    if command_exists git; then
        echo -e "  ${GREEN}${CHECK_MARK} git${NC}"
    else
        echo -e "  ${RED}${CROSS_MARK} git not found${NC}"
        echo -e "  ${YELLOW}Please install git${NC}"
        exit 1
    fi
    
    # Check for ZoKrates (optional)
    if command_exists zokrates; then
        echo -e "  ${GREEN}${CHECK_MARK} ZoKrates${NC}"
        ZOKRATES_INSTALLED=true
    else
        echo -e "  ${YELLOW}? ZoKrates not found (optional, will be installed)${NC}"
        ZOKRATES_INSTALLED=false
    fi
    
    # Check for Apple Silicon
    if [ "$OS" = "Darwin" ] && [ "$ARCH" = "arm64" ]; then
        echo -e "  ${GREEN}${CHECK_MARK} Apple Silicon detected${NC}"
        APPLE_SILICON=true
    else
        echo -e "  ${YELLOW}? Not running on Apple Silicon (MLX acceleration disabled)${NC}"
        APPLE_SILICON=false
    fi
    
    echo ""
}

# Install ZoKrates
install_zokrates() {
    if [ "$ZOKRATES_INSTALLED" = true ]; then
        echo -e "${GREEN}ZoKrates already installed, skipping...${NC}"
        return
    fi
    
    echo -e "${BLUE}${BOLD}Installing ZoKrates...${NC}"
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Download ZoKrates
    if [ "$OS" = "Darwin" ]; then
        if [ "$ARCH" = "arm64" ]; then
            echo -e "  ${YELLOW}Downloading ZoKrates for macOS ARM64...${NC}"
            curl -L -o zokrates.tar.gz "https://github.com/ZoKrates/ZoKrates/releases/download/0.8.0/zokrates-0.8.0-aarch64-apple-darwin.tar.gz"
        else
            echo -e "  ${YELLOW}Downloading ZoKrates for macOS x86_64...${NC}"
            curl -L -o zokrates.tar.gz "https://github.com/ZoKrates/ZoKrates/releases/download/0.8.0/zokrates-0.8.0-x86_64-apple-darwin.tar.gz"
        fi
    elif [ "$OS" = "Linux" ]; then
        echo -e "  ${YELLOW}Downloading ZoKrates for Linux...${NC}"
        curl -L -o zokrates.tar.gz "https://github.com/ZoKrates/ZoKrates/releases/download/0.8.0/zokrates-0.8.0-x86_64-unknown-linux-gnu.tar.gz"
    else
        echo -e "  ${RED}Unsupported OS: $OS${NC}"
        echo -e "  ${YELLOW}Please install ZoKrates manually: https://zokrates.github.io/gettingstarted.html${NC}"
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        return
    fi
    
    # Extract ZoKrates
    tar -xzf zokrates.tar.gz
    
    # Install ZoKrates
    mkdir -p "$INSTALL_DIR/bin"
    cp zokrates "$INSTALL_DIR/bin/"
    
    # Add to PATH
    echo -e "  ${YELLOW}Adding ZoKrates to PATH...${NC}"
    echo 'export PATH="$PATH:$HOME/.llamaverifier/bin"' >> "$HOME/.bashrc"
    echo 'export PATH="$PATH:$HOME/.llamaverifier/bin"' >> "$HOME/.zshrc"
    
    # Clean up
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
    echo -e "  ${GREEN}${CHECK_MARK} ZoKrates installed successfully${NC}"
    echo ""
}

# Clone repository
clone_repository() {
    echo -e "${BLUE}${BOLD}Cloning LlamaVerifier repository...${NC}"
    
    if [ -d "$INSTALL_DIR/repo" ]; then
        echo -e "  ${YELLOW}Repository already exists, updating...${NC}"
        cd "$INSTALL_DIR/repo"
        git pull
        cd - > /dev/null
    else
        echo -e "  ${YELLOW}Cloning repository...${NC}"
        mkdir -p "$INSTALL_DIR/repo"
        git clone "$REPO_URL" "$INSTALL_DIR/repo"
    fi
    
    echo -e "  ${GREEN}${CHECK_MARK} Repository cloned/updated successfully${NC}"
    echo ""
}

# Install Python dependencies
install_dependencies() {
    echo -e "${BLUE}${BOLD}Installing Python dependencies...${NC}"
    
    cd "$INSTALL_DIR/repo"
    
    # Create virtual environment
    echo -e "  ${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$INSTALL_DIR/venv"
    
    # Activate virtual environment
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Upgrade pip
    echo -e "  ${YELLOW}Upgrading pip...${NC}"
    pip3 install --upgrade pip
    
    # Install dependencies
    echo -e "  ${YELLOW}Installing dependencies...${NC}"
    pip3 install -e .
    
    # Install MLX if on Apple Silicon
    if [ "$APPLE_SILICON" = true ]; then
        echo -e "  ${YELLOW}Installing MLX for Apple Silicon acceleration...${NC}"
        pip3 install -e ".[apple]"
    fi
    
    # Install development dependencies
    echo -e "  ${YELLOW}Installing development dependencies...${NC}"
    pip3 install -e ".[dev]"
    
    # Deactivate virtual environment
    deactivate
    
    echo -e "  ${GREEN}${CHECK_MARK} Dependencies installed successfully${NC}"
    echo ""
}

# Create shell wrapper
create_shell_wrapper() {
    echo -e "${BLUE}${BOLD}Creating shell wrapper...${NC}"
    
    # Create bin directory
    mkdir -p "$INSTALL_DIR/bin"
    
    # Create wrapper script
    cat > "$INSTALL_DIR/bin/llamaverifier" << EOF
#!/bin/bash
# LlamaVerifier shell wrapper

# Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Run LlamaVerifier
python -m llamaverifier.cli.commands "\$@"

# Deactivate virtual environment
deactivate
EOF
    
    # Make wrapper executable
    chmod +x "$INSTALL_DIR/bin/llamaverifier"
    
    # Add to PATH
    echo -e "  ${YELLOW}Adding LlamaVerifier to PATH...${NC}"
    echo 'export PATH="$PATH:$HOME/.llamaverifier/bin"' >> "$HOME/.bashrc"
    echo 'export PATH="$PATH:$HOME/.llamaverifier/bin"' >> "$HOME/.zshrc"
    
    echo -e "  ${GREEN}${CHECK_MARK} Shell wrapper created successfully${NC}"
    echo ""
}

# Print completion message
print_completion() {
    echo -e "${GREEN}${BOLD}${LLAMA} LlamaVerifier installed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}To use LlamaVerifier, restart your terminal or run:${NC}"
    echo -e "  ${CYAN}export PATH=\"\$PATH:\$HOME/.llamaverifier/bin\"${NC}"
    echo ""
    echo -e "${YELLOW}Then you can run:${NC}"
    echo -e "  ${CYAN}llamaverifier --help${NC}"
    echo ""
    echo -e "${YELLOW}For more information, visit:${NC}"
    echo -e "  ${CYAN}https://github.com/username/llamaverifier${NC}"
    echo ""
}

# Main installation function
main() {
    print_banner
    check_requirements
    install_zokrates
    clone_repository
    install_dependencies
    create_shell_wrapper
    print_completion
}

# Run main function
main 