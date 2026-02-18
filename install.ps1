# Kachi Installation Script for Windows
# This script downloads and installs the latest release of Kachi for Windows x64 systems
# For other platforms, please download manually from https://github.com/EndlessTrax/kachi/releases

$ErrorActionPreference = 'Stop'

$REPO_OWNER = "EndlessTrax"
$REPO_NAME = "kachi"
$INSTALL_DIR = Join-Path $env:USERPROFILE ".local\bin"
$BINARY_NAME = "kachi.exe"

# Print colored messages
function Print-Info {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

# Detect architecture
function Get-Architecture {
    $arch = $env:PROCESSOR_ARCHITECTURE
    
    switch ($arch) {
        "AMD64" {
            return "x64"
        }
        "ARM64" {
            Print-Error "ARM64 architecture is not currently supported. Please check https://github.com/$REPO_OWNER/$REPO_NAME/releases for available platforms."
            exit 1
        }
        default {
            Print-Error "Unsupported architecture: $arch"
            exit 1
        }
    }
}

# Get the latest release version from GitHub API
function Get-LatestVersion {
    $apiUrl = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"
    
    try {
        # Try to fetch from GitHub API
        $response = Invoke-WebRequest -Uri $apiUrl -UseBasicParsing -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 200) {
            $json = $response.Content | ConvertFrom-Json
            return $json.tag_name
        }
    }
    catch {
        # API fetch failed, try fallback
    }
    
    # Fallback: try to scrape from releases page
    try {
        $releasesPage = "https://github.com/$REPO_OWNER/$REPO_NAME/releases/latest"
        $response = Invoke-WebRequest -Uri $releasesPage -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue
        
        if ($response.Headers.Location) {
            $location = $response.Headers.Location
            if ($location -match '/tag/(.+)$') {
                return $matches[1]
            }
        }
    }
    catch {
        if ($_.Exception.Response.Headers.Location) {
            $location = $_.Exception.Response.Headers.Location.AbsoluteUri
            if ($location -match '/tag/(.+)$') {
                return $matches[1]
            }
        }
    }
    
    return $null
}

# Download and install the binary
function Install-Binary {
    param(
        [string]$Platform,
        [string]$Version
    )
    
    $binaryName = "$REPO_NAME-$Version-$Platform.exe"
    $downloadUrl = "https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/$Version/$binaryName"
    $tempFile = Join-Path $env:TEMP $binaryName
    
    Print-Info "Downloading $REPO_NAME $Version for $Platform..."
    
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing
    }
    catch {
        Print-Error "Failed to download from $downloadUrl"
        Print-Error $_.Exception.Message
        exit 1
    }
    
    # Create install directory if it doesn't exist
    if (-not (Test-Path -Path $INSTALL_DIR)) {
        Print-Info "Creating directory $INSTALL_DIR..."
        New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
    }
    
    # Install the binary
    $installPath = Join-Path $INSTALL_DIR $BINARY_NAME
    
    if (Test-Path -Path $installPath) {
        Print-Warning "Existing installation found at $installPath, overwriting..."
    }
    
    Print-Info "Installing to $installPath..."
    Move-Item -Path $tempFile -Destination $installPath -Force
    
    Print-Info "Successfully installed $REPO_NAME $Version"
    Write-Host ""
    
    # Check if the install directory is in PATH
    $pathDirs = $env:PATH -split ';'
    $installDirInPath = $pathDirs | Where-Object { $_ -eq $INSTALL_DIR }
    
    if (-not $installDirInPath) {
        Print-Warning "$INSTALL_DIR is not in your PATH."
        Write-Host "To use $BINARY_NAME, add the following directory to your PATH:"
        Write-Host ""
        Write-Host "    $INSTALL_DIR"
        Write-Host ""
        Write-Host "You can add it to your PATH by running this command in PowerShell (as Administrator):"
        Write-Host ""
        Write-Host '    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";' + $INSTALL_DIR + '", "User")'
        Write-Host ""
        Write-Host "After running this command, restart your terminal for changes to take effect."
        Write-Host ""
    }
    else {
        Print-Info "You can now use the '$BINARY_NAME' command."
    }
}

# Main installation process
function Main {
    Print-Info "Starting $REPO_NAME installation..."
    
    # Detect architecture
    $arch = Get-Architecture
    $platform = "windows-$arch"
    Print-Info "Detected platform: $platform"
    
    # Get latest version
    $version = Get-LatestVersion
    
    if (-not $version) {
        Print-Error "Failed to fetch the latest version. Please check your internet connection."
        exit 1
    }
    
    Print-Info "Latest version: $version"
    
    # Download and install
    Install-Binary -Platform $platform -Version $version
}

# Run main function
Main
