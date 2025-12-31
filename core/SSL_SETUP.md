# SSL/HTTPS Setup for Local Development

This guide will help you set up HTTPS for your Django development server with trusted SSL certificates.

## Why Use HTTPS in Development?

- **Match Production Environment**: Develop with the same protocols you'll use in production
- **Test Security Features**: Test secure cookies, HSTS, and other HTTPS-only features
- **Modern Browser APIs**: Many browser APIs (like Service Workers, Geolocation, etc.) require HTTPS
- **No Mixed Content Warnings**: Avoid warnings when loading HTTPS resources
- **Better Security Testing**: Test your application's security in a realistic environment

## Quick Start

### Method 1: Using Django Management Command (Recommended)

The easiest way to set up SSL certificates:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate SSL certificates
python manage.py setup_ssl

# Run the SSL server
python manage.py runsslserver --certificate certs/localhost.crt --key certs/localhost.key
```

Visit: **https://127.0.0.1:8000**

### Method 2: Using Shell Scripts

#### On Linux/macOS:

```bash
# Make the script executable
chmod +x setup_ssl_certs.sh

# Run the script
./setup_ssl_certs.sh

# Run the SSL server
python manage.py runsslserver --certificate certs/localhost.crt --key certs/localhost.key
```

#### On Windows (PowerShell):

```powershell
# Run as Administrator (optional, for mkcert CA installation)
.\setup_ssl_certs.ps1

# Run the SSL server
python manage.py runsslserver --certificate certs/localhost.crt --key certs/localhost.key
```

## Installation Methods

### Option 1: mkcert (Recommended - Trusted Certificates)

**mkcert** generates locally-trusted SSL certificates. Your browser won't show any warnings!

#### Installation:

**macOS:**
```bash
brew install mkcert
```

**Windows:**
```powershell
# Using Chocolatey
choco install mkcert

# Using Scoop
scoop bucket add extras
scoop install mkcert
```

**Linux:**
```bash
# Arch Linux
sudo pacman -S mkcert

# Ubuntu/Debian (using Homebrew on Linux)
brew install mkcert

# Or download from GitHub releases
# https://github.com/FiloSottile/mkcert/releases
```

#### Usage:

```bash
# The setup script will automatically use mkcert if installed
python manage.py setup_ssl
```

**What happens:**
1. mkcert installs a local Certificate Authority (CA) in your system
2. Generates certificates signed by this CA
3. Your browser automatically trusts these certificates
4. **No security warnings!** ✅

### Option 2: OpenSSL (Fallback - Self-Signed Certificates)

If mkcert is not available, the setup scripts will automatically fall back to OpenSSL.

**Note:** OpenSSL generates self-signed certificates that browsers don't trust by default. You'll see security warnings.

#### What to expect:
- ⚠️ Browser will show "Your connection is not private"
- You'll need to click "Advanced" → "Proceed to 127.0.0.1"
- This is normal for self-signed certificates

#### To trust OpenSSL certificates (optional):

**Chrome/Edge:**
1. Visit `https://127.0.0.1:8000`
2. Click on "Not Secure" in the address bar
3. Click "Certificate" → "Details" → "Export"
4. Import to system trust store

**Firefox:**
1. Visit `https://127.0.0.1:8000`
2. Click "Advanced" → "Accept the Risk and Continue"

## Command Reference

### Setup SSL Certificates

```bash
# Basic setup (auto-detects method)
python manage.py setup_ssl

# Force regenerate existing certificates
python manage.py setup_ssl --force

# Use specific method
python manage.py setup_ssl --method mkcert
python manage.py setup_ssl --method openssl
```

### Run SSL Server

```bash
# With custom certificates
python manage.py runsslserver --certificate certs/localhost.crt --key certs/localhost.key

# With custom port
python manage.py runsslserver 0.0.0.0:8443 --certificate certs/localhost.crt --key certs/localhost.key

# Using default certificates (from django-sslserver package)
python manage.py runsslserver
```

## Project Structure

After setup, your project will have:

```
core/
├── certs/                          # SSL certificates directory
│   ├── .gitignore                 # Prevents committing certificates
│   ├── localhost.crt              # SSL certificate (auto-generated)
│   └── localhost.key              # Private key (auto-generated)
├── core/
│   └── management/
│       └── commands/
│           └── setup_ssl.py       # Django management command
├── setup_ssl_certs.sh             # Bash setup script
├── setup_ssl_certs.ps1            # PowerShell setup script
└── SSL_SETUP.md                   # This documentation
```

## Troubleshooting

### "NET::ERR_CERT_AUTHORITY_INVALID" in Chrome

**If using mkcert:**
- This shouldn't happen with mkcert
- Try reinstalling: `mkcert -install`
- Check mkcert CA: `mkcert -CAROOT`

**If using OpenSSL:**
- This is expected with self-signed certificates
- Click "Advanced" → "Proceed to 127.0.0.1 (unsafe)"
- Or install mkcert for trusted certificates

### "This site can't provide a secure connection"

- Make sure you're using `https://` not `http://`
- Verify certificates exist: `ls certs/`
- Regenerate certificates: `python manage.py setup_ssl --force`

### Port Already in Use

```bash
# Check what's using port 8000
# Linux/macOS:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Use a different port
python manage.py runsslserver 0.0.0.0:8443 --certificate certs/localhost.crt --key certs/localhost.key
```

### Permission Denied (Linux/macOS)

```bash
# Make scripts executable
chmod +x setup_ssl_certs.sh

# Run as root if needed (for installing CA)
sudo python manage.py setup_ssl
```

### Windows PowerShell Execution Policy

```powershell
# If you can't run .ps1 scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the script
.\setup_ssl_certs.ps1
```

## Security Best Practices

### ✅ DO:
- Use mkcert for local development (trusted certificates)
- Keep your private keys (`*.key`) secure and never commit them
- Regenerate certificates periodically
- Use HTTPS in development to match production
- Test your app's security features with HTTPS

### ❌ DON'T:
- **Never** commit SSL certificates or private keys to version control
- **Never** use development certificates in production
- **Never** share your private keys
- **Never** disable SSL verification in production code
- **Never** use self-signed certificates in production

## Git Configuration

The `certs/.gitignore` file prevents accidentally committing certificates:

```gitignore
*.crt
*.key
*.pem
```

**Always verify before committing:**
```bash
git status
# Make sure no .crt or .key files are listed
```

## Production Deployment

**Important:** These certificates are for **development only**!

For production, use:
- **Let's Encrypt** (free, automated SSL certificates)
- **Cloudflare** (free SSL/TLS with CDN)
- **Commercial SSL certificates** from trusted CAs
- **AWS Certificate Manager** (if using AWS)

Never use development certificates in production!

## Additional Resources

- [mkcert GitHub](https://github.com/FiloSottile/mkcert)
- [django-sslserver Documentation](https://github.com/teddziuba/django-sslserver)
- [Let's Encrypt](https://letsencrypt.org/) (for production)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)

## Support

If you encounter issues:

1. Check this documentation
2. Verify your setup:
   ```bash
   python manage.py setup_ssl --force
   ls -la certs/
   ```
3. Check the Django server output for errors
4. Review your browser's certificate details

## License

This setup is part of your Django project and follows your project's license.

---

**Happy Secure Development! 🔒**
