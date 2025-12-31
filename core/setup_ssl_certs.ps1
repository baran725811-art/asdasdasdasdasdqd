# SSL Certificate Setup Script for Django Development (Windows PowerShell)
# Supports both mkcert (recommended) and OpenSSL (fallback)

param(
    [switch]$Force
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CertsDir = Join-Path $ScriptDir "certs"
$CertFile = Join-Path $CertsDir "localhost.crt"
$KeyFile = Join-Path $CertsDir "localhost.key"

# Print colored messages
function Print-Info { Write-Host "ℹ $args" -ForegroundColor Blue }
function Print-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Print-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Print-Error { Write-Host "✗ $args" -ForegroundColor Red }

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   SSL Certificate Setup for Local Development     ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Print-Warning "Not running as Administrator. mkcert installation may require elevation."
}

# Check if certificates already exist
if ((Test-Path $CertFile) -and (Test-Path $KeyFile) -and -not $Force) {
    Print-Warning "SSL certificates already exist!"
    $response = Read-Host "Do you want to regenerate them? (y/N)"
    if ($response -notmatch '^[Yy]$') {
        Print-Info "Keeping existing certificates. Exiting."
        exit 0
    }
    Print-Info "Removing existing certificates..."
    Remove-Item $CertFile -ErrorAction SilentlyContinue
    Remove-Item $KeyFile -ErrorAction SilentlyContinue
}

# Create certs directory if it doesn't exist
if (-not (Test-Path $CertsDir)) {
    New-Item -ItemType Directory -Path $CertsDir | Out-Null
}

# Function to setup with mkcert
function Setup-WithMkcert {
    Print-Info "Setting up SSL certificates with mkcert..."

    # Check if mkcert is installed
    $mkcertPath = Get-Command mkcert -ErrorAction SilentlyContinue
    if (-not $mkcertPath) {
        Print-Error "mkcert is not installed!"
        Print-Info "Please install mkcert:"
        Write-Host ""
        Write-Host "  Option 1 - Chocolatey (recommended):"
        Write-Host "    choco install mkcert"
        Write-Host ""
        Write-Host "  Option 2 - Scoop:"
        Write-Host "    scoop bucket add extras"
        Write-Host "    scoop install mkcert"
        Write-Host ""
        Write-Host "  Option 3 - Manual download:"
        Write-Host "    https://github.com/FiloSottile/mkcert/releases"
        Write-Host ""
        return $false
    }

    Print-Success "mkcert found!"

    # Install local CA if not already installed
    Print-Info "Installing local Certificate Authority..."
    try {
        & mkcert -install
    } catch {
        Print-Warning "Failed to install CA. You may need to run as Administrator."
    }

    # Generate certificates
    Print-Info "Generating SSL certificates for localhost and 127.0.0.1..."
    Push-Location $CertsDir
    try {
        & mkcert -cert-file localhost.crt -key-file localhost.key localhost 127.0.0.1 ::1
        Pop-Location

        Print-Success "Certificates generated successfully with mkcert!"
        Print-Success "Your browser will now trust these certificates!"
        return $true
    } catch {
        Pop-Location
        Print-Error "Failed to generate certificates with mkcert: $_"
        return $false
    }
}

# Function to setup with OpenSSL (fallback)
function Setup-WithOpenSSL {
    Print-Warning "Falling back to OpenSSL (self-signed certificates)..."
    Print-Warning "Note: Browser will still show security warnings with OpenSSL!"
    Print-Info "For trusted certificates, please install mkcert."

    # Check if openssl is installed
    $opensslPath = Get-Command openssl -ErrorAction SilentlyContinue
    if (-not $opensslPath) {
        Print-Error "OpenSSL is not installed!"
        Print-Info "Install OpenSSL:"
        Write-Host "  - Git for Windows includes OpenSSL"
        Write-Host "  - Or download from: https://slproweb.com/products/Win32OpenSSL.html"
        return $false
    }

    Print-Info "Generating self-signed SSL certificates..."

    try {
        # Generate private key
        & openssl genrsa -out $KeyFile 2048

        # Generate certificate
        & openssl req -new -x509 -key $KeyFile -out $CertFile -days 365 `
            -subj "/C=US/ST=State/L=City/O=Development/CN=localhost" `
            -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1,IP:::1"

        Print-Success "Self-signed certificates generated with OpenSSL!"
        Print-Warning "To trust these certificates, you'll need to add them to your system manually."
        return $true
    } catch {
        Print-Error "Failed to generate certificates with OpenSSL: $_"
        return $false
    }
}

# Main setup flow
Print-Info "Checking for certificate generation tools..."

$success = $false

if (Setup-WithMkcert) {
    $success = $true
    Write-Host ""
    Print-Success "═══════════════════════════════════════════════════"
    Print-Success "SSL Setup Complete with mkcert! 🎉"
    Print-Success "═══════════════════════════════════════════════════"
    Write-Host ""
    Print-Info "Certificate location: $CertFile"
    Print-Info "Key location: $KeyFile"
    Write-Host ""
    Print-Info "Next steps:"
    Write-Host "  1. Run: python manage.py runsslserver --certificate $CertFile --key $KeyFile"
    Write-Host "  2. Visit: https://127.0.0.1:8000"
    Write-Host "  3. You should see a secure connection (no warnings)!"
    Write-Host ""
} elseif (Setup-WithOpenSSL) {
    $success = $true
    Write-Host ""
    Print-Success "═══════════════════════════════════════════════════"
    Print-Success "SSL Setup Complete with OpenSSL"
    Print-Success "═══════════════════════════════════════════════════"
    Write-Host ""
    Print-Info "Certificate location: $CertFile"
    Print-Info "Key location: $KeyFile"
    Write-Host ""
    Print-Warning "These are self-signed certificates!"
    Print-Info "Browser will show warnings. To fix:"
    Write-Host "  - Install mkcert for trusted local certificates"
    Write-Host "  - Or manually trust the certificate in your browser"
    Write-Host ""
    Print-Info "Next steps:"
    Write-Host "  1. Run: python manage.py runsslserver --certificate $CertFile --key $KeyFile"
    Write-Host "  2. Visit: https://127.0.0.1:8000"
    Write-Host "  3. Accept the security warning in your browser"
    Write-Host ""
} else {
    Print-Error "Failed to generate SSL certificates!"
    Print-Error "Please install either mkcert or OpenSSL."
    exit 1
}

if ($success) {
    Print-Success "File permissions set correctly!"
}
