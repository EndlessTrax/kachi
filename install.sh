#!/bin/bash
set -e

# Kachi Installation Script
# This script downloads and installs the latest release of Kachi

REPO_OWNER="EndlessTrax"
REPO_NAME="kachi"
INSTALL_DIR="${HOME}/.local/bin"
BINARY_NAME="kachi"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Detect OS and architecture
detect_platform() {
    local os=""
    local arch=""
    
    # Detect OS
    case "$(uname -s)" in
        Linux*)
            os="linux"
            ;;
        Darwin*)
            print_error "macOS is not currently supported. Please check https://github.com/${REPO_OWNER}/${REPO_NAME}/releases for available platforms."
            exit 1
            ;;
        MINGW*|MSYS*|CYGWIN*)
            print_error "Windows installation via this script is not supported. Please download the .exe from https://github.com/${REPO_OWNER}/${REPO_NAME}/releases"
            exit 1
            ;;
        *)
            print_error "Unsupported operating system: $(uname -s)"
            exit 1
            ;;
    esac
    
    # Detect architecture
    case "$(uname -m)" in
        x86_64|amd64)
            arch="x64"
            ;;
        aarch64|arm64)
            print_error "ARM64 architecture is not currently supported. Please check https://github.com/${REPO_OWNER}/${REPO_NAME}/releases for available platforms."
            exit 1
            ;;
        *)
            print_error "Unsupported architecture: $(uname -m)"
            exit 1
            ;;
    esac
    
    echo "${os}-${arch}"
}

# Get the latest release version from GitHub API
get_latest_version() {
    local api_url="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest"
    
    if ! command -v curl >/dev/null 2>&1; then
        print_error "curl is required but not installed. Please install curl and try again."
        exit 1
    fi
    
    # Try to fetch from GitHub API with proper error handling
    local response
    response=$(curl -s -w "\n%{http_code}" "${api_url}" 2>/dev/null)
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo "$body" | grep '"tag_name"' | sed -E 's/.*"tag_name": "([^"]+)".*/\1/'
    else
        # Fallback: try to scrape from releases page
        local releases_page="https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/latest"
        local version
        version=$(curl -sL -o /dev/null -w '%{url_effective}' "${releases_page}" 2>/dev/null | sed 's|.*/tag/||')
        
        if [ -n "$version" ]; then
            echo "$version"
        else
            return 1
        fi
    fi
}

# Download and install the binary
install_binary() {
    local platform="$1"
    local version="$2"
    
    local binary_name="${REPO_NAME}-${version}-${platform}"
    local download_url="https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/download/${version}/${binary_name}"
    local temp_file="/tmp/${binary_name}"
    
    print_info "Downloading ${REPO_NAME} ${version} for ${platform}..."
    
    if ! curl -L -f -s -S -o "${temp_file}" "${download_url}"; then
        print_error "Failed to download from ${download_url}"
        exit 1
    fi
    
    # Create install directory if it doesn't exist
    if [ ! -d "${INSTALL_DIR}" ]; then
        print_info "Creating directory ${INSTALL_DIR}..."
        mkdir -p "${INSTALL_DIR}"
    fi
    
    # Install the binary
    local install_path="${INSTALL_DIR}/${BINARY_NAME}"
    
    if [ -f "${install_path}" ]; then
        print_warning "Existing installation found at ${install_path}, overwriting..."
    fi
    
    print_info "Installing to ${install_path}..."
    mv "${temp_file}" "${install_path}"
    chmod +x "${install_path}"
    
    print_info "Successfully installed ${REPO_NAME} ${version}"
    echo ""
    
    # Check if the install directory is in PATH
    if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
        print_warning "${INSTALL_DIR} is not in your PATH."
        echo "To use ${BINARY_NAME}, add the following to your shell configuration file (.bashrc, .zshrc, etc.):"
        echo ""
        echo "    export PATH=\"\$PATH:${INSTALL_DIR}\""
        echo ""
    else
        print_info "You can now use the '${BINARY_NAME}' command."
    fi
}

# Main installation process
main() {
    print_info "Starting ${REPO_NAME} installation..."
    
    # Detect platform
    local platform
    platform=$(detect_platform)
    print_info "Detected platform: ${platform}"
    
    # Get latest version
    local version
    version=$(get_latest_version)
    
    if [ -z "${version}" ]; then
        print_error "Failed to fetch the latest version. Please check your internet connection."
        exit 1
    fi
    
    print_info "Latest version: ${version}"
    
    # Download and install
    install_binary "${platform}" "${version}"
}

# Run main function
main
