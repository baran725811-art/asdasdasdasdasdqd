# SSL Certificates Directory

This directory contains SSL certificates for local HTTPS development.

## Contents

After running the setup, this directory will contain:

- `localhost.crt` - SSL certificate for localhost
- `localhost.key` - Private key for the certificate
- `.gitignore` - Prevents committing certificates to git

## Setup

Generate certificates using any of these methods:

### Method 1: Django Management Command
```bash
python manage.py setup_ssl
```

### Method 2: Shell Script (Linux/macOS)
```bash
./setup_ssl_certs.sh
```

### Method 3: PowerShell Script (Windows)
```powershell
.\setup_ssl_certs.ps1
```

## Usage

After generating certificates:

```bash
python manage.py runsslserver --certificate certs/localhost.crt --key certs/localhost.key
```

Then visit: **https://127.0.0.1:8000**

## Security

⚠️ **IMPORTANT:**
- These certificates are for **development only**
- Never commit certificates or keys to version control
- Never use development certificates in production
- Regenerate periodically for security

## Documentation

See [SSL_SETUP.md](../SSL_SETUP.md) for complete documentation.
