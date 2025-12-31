#!/bin/bash

# SSL Certificate Setup Script for Django Development
# Supports both mkcert (recommended) and OpenSSL (fallback)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$SCRIPT_DIR/certs"
CERT_FILE="$CERTS_DIR/localhost.crt"
KEY_FILE="$CERTS_DIR/localhost.key"

# Print colored messages
print_info() { echo -e "${BLUE}ℹ ${1}${NC}"; }
print_success() { echo -e "${GREEN}✓ ${1}${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ ${1}${NC}"; }
print_error() { echo -e "${RED}✗ ${1}${NC}"; }

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║   SSL Certificate Setup for Local Development     ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if certificates already exist
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    print_warning "SSL certificates already exist!"
    read -p "Do you want to regenerate them? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Keeping existing certificates. Exiting."
        exit 0
    fi
    print_info "Removing existing certificates..."
    rm -f "$CERT_FILE" "$KEY_FILE"
fi

# Create certs directory if it doesn't exist
mkdir -p "$CERTS_DIR"

# Function to setup with mkcert
setup_with_mkcert() {
    print_info "Setting up SSL certificates with mkcert..."

    # Check if mkcert is installed
    if ! command -v mkcert &> /dev/null; then
        print_error "mkcert is not installed!"
        print_info "Please install mkcert:"
        echo ""
        echo "  macOS:   brew install mkcert"
        echo "  Linux:   https://github.com/FiloSottile/mkcert#installation"
        echo "  Windows: choco install mkcert"
        echo ""
        return 1
    fi

    print_success "mkcert found!"

    # Install local CA if not already installed
    print_info "Installing local Certificate Authority..."
    mkcert -install

    # Generate certificates
    print_info "Generating SSL certificates for localhost and 127.0.0.1..."
    cd "$CERTS_DIR"
    mkcert -cert-file localhost.crt -key-file localhost.key localhost 127.0.0.1 ::1

    print_success "Certificates generated successfully with mkcert!"
    print_success "Your browser will now trust these certificates!"

    return 0
}

# Function to setup with OpenSSL (fallback)
setup_with_openssl() {
    print_warning "Falling back to OpenSSL (self-signed certificates)..."
    print_warning "Note: Browser will still show security warnings with OpenSSL!"
    print_info "For trusted certificates, please install mkcert."

    # Check if openssl is installed
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed!"
        return 1
    fi

    print_info "Generating self-signed SSL certificates..."

    # Generate private key
    openssl genrsa -out "$KEY_FILE" 2048

    # Generate certificate
    openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" -days 365 \
        -subj "/C=US/ST=State/L=City/O=Development/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1,IP:::1"

    print_success "Self-signed certificates generated with OpenSSL!"
    print_warning "To trust these certificates, you'll need to add them to your system manually."

    return 0
}

# Main setup flow
print_info "Checking for certificate generation tools..."

if setup_with_mkcert; then
    echo ""
    print_success "═══════════════════════════════════════════════════"
    print_success "SSL Setup Complete with mkcert! 🎉"
    print_success "═══════════════════════════════════════════════════"
    echo ""
    print_info "Certificate location: $CERT_FILE"
    print_info "Key location: $KEY_FILE"
    echo ""
    print_info "Next steps:"
    echo "  1. Run: python manage.py runsslserver"
    echo "  2. Visit: https://127.0.0.1:8000"
    echo "  3. You should see a secure connection (no warnings)!"
    echo ""
elif setup_with_openssl; then
    echo ""
    print_success "═══════════════════════════════════════════════════"
    print_success "SSL Setup Complete with OpenSSL"
    print_success "═══════════════════════════════════════════════════"
    echo ""
    print_info "Certificate location: $CERT_FILE"
    print_info "Key location: $KEY_FILE"
    echo ""
    print_warning "These are self-signed certificates!"
    print_info "Browser will show warnings. To fix:"
    echo "  - Install mkcert for trusted local certificates"
    echo "  - Or manually trust the certificate in your browser"
    echo ""
    print_info "Next steps:"
    echo "  1. Run: python manage.py runsslserver"
    echo "  2. Visit: https://127.0.0.1:8000"
    echo "  3. Accept the security warning in your browser"
    echo ""
else
    print_error "Failed to generate SSL certificates!"
    print_error "Please install either mkcert or OpenSSL."
    exit 1
fi

# Set proper permissions
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

print_success "File permissions set correctly!"
