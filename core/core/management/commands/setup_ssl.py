"""
Django Management Command: setup_ssl
Generates SSL certificates for local HTTPS development
"""

import os
import subprocess
import sys
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate SSL certificates for local HTTPS development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of existing certificates',
        )
        parser.add_argument(
            '--method',
            type=str,
            choices=['mkcert', 'openssl', 'auto'],
            default='auto',
            help='Certificate generation method (default: auto)',
        )

    def handle(self, *args, **options):
        self.force = options['force']
        self.method = options['method']

        # Print banner
        self.print_banner()

        # Setup certificates directory
        self.certs_dir = Path(settings.BASE_DIR) / 'certs'
        self.cert_file = self.certs_dir / 'localhost.crt'
        self.key_file = self.certs_dir / 'localhost.key'

        # Create certs directory
        self.create_certs_directory()

        # Check existing certificates
        if self.check_existing_certificates():
            return

        # Generate certificates
        self.generate_certificates()

        # Print completion message
        self.print_completion()

    def print_banner(self):
        """Print a fancy banner"""
        self.stdout.write(self.style.HTTP_INFO(''))
        self.stdout.write(self.style.HTTP_INFO('╔════════════════════════════════════════════════════╗'))
        self.stdout.write(self.style.HTTP_INFO('║   SSL Certificate Setup for Local Development     ║'))
        self.stdout.write(self.style.HTTP_INFO('╚════════════════════════════════════════════════════╝'))
        self.stdout.write(self.style.HTTP_INFO(''))

    def create_certs_directory(self):
        """Create certificates directory and .gitignore"""
        if not self.certs_dir.exists():
            self.certs_dir.mkdir(parents=True)
            self.stdout.write(self.style.SUCCESS(f'✓ Created directory: {self.certs_dir}'))

        # Create .gitignore
        gitignore_file = self.certs_dir / '.gitignore'
        if not gitignore_file.exists():
            gitignore_content = "*.crt\n*.key\n*.pem\n"
            gitignore_file.write_text(gitignore_content)
            self.stdout.write(self.style.SUCCESS('✓ Created .gitignore for certificates'))

    def check_existing_certificates(self):
        """Check if certificates already exist"""
        if self.cert_file.exists() and self.key_file.exists():
            if not self.force:
                self.stdout.write(self.style.WARNING('⚠ SSL certificates already exist!'))
                self.stdout.write(self.style.WARNING(f'  Certificate: {self.cert_file}'))
                self.stdout.write(self.style.WARNING(f'  Key: {self.key_file}'))
                self.stdout.write('')
                self.stdout.write(self.style.NOTICE('Use --force to regenerate certificates'))
                return True
            else:
                self.stdout.write(self.style.WARNING('⚠ Removing existing certificates...'))
                self.cert_file.unlink()
                self.key_file.unlink()
        return False

    def command_exists(self, command):
        """Check if a command exists in PATH"""
        try:
            subprocess.run([command, '--version'],
                         capture_output=True,
                         check=False)
            return True
        except FileNotFoundError:
            return False

    def generate_certificates(self):
        """Generate SSL certificates using available method"""
        if self.method == 'auto':
            # Try mkcert first, fallback to openssl
            if self.command_exists('mkcert'):
                self.generate_with_mkcert()
            elif self.command_exists('openssl'):
                self.generate_with_openssl()
            else:
                raise CommandError(
                    'Neither mkcert nor OpenSSL found!\n'
                    'Please install one of them:\n'
                    '  - mkcert (recommended): https://github.com/FiloSottile/mkcert\n'
                    '  - OpenSSL: Usually pre-installed on most systems'
                )
        elif self.method == 'mkcert':
            if not self.command_exists('mkcert'):
                raise CommandError('mkcert not found! Install it from: https://github.com/FiloSottile/mkcert')
            self.generate_with_mkcert()
        elif self.method == 'openssl':
            if not self.command_exists('openssl'):
                raise CommandError('OpenSSL not found!')
            self.generate_with_openssl()

    def generate_with_mkcert(self):
        """Generate certificates using mkcert (trusted)"""
        self.stdout.write(self.style.HTTP_INFO('ℹ Setting up SSL certificates with mkcert...'))

        try:
            # Install local CA
            self.stdout.write(self.style.HTTP_INFO('ℹ Installing local Certificate Authority...'))
            subprocess.run(['mkcert', '-install'], check=True, capture_output=True)

            # Generate certificates
            self.stdout.write(self.style.HTTP_INFO('ℹ Generating SSL certificates...'))
            subprocess.run([
                'mkcert',
                '-cert-file', str(self.cert_file),
                '-key-file', str(self.key_file),
                'localhost', '127.0.0.1', '::1'
            ], check=True, capture_output=True, cwd=str(self.certs_dir))

            self.stdout.write(self.style.SUCCESS('✓ Certificates generated successfully with mkcert!'))
            self.stdout.write(self.style.SUCCESS('✓ Your browser will now trust these certificates!'))
            self.cert_method = 'mkcert'

        except subprocess.CalledProcessError as e:
            raise CommandError(f'Failed to generate certificates with mkcert: {e}')

    def generate_with_openssl(self):
        """Generate self-signed certificates using OpenSSL"""
        self.stdout.write(self.style.WARNING('⚠ Falling back to OpenSSL (self-signed certificates)'))
        self.stdout.write(self.style.WARNING('⚠ Note: Browser will still show security warnings!'))
        self.stdout.write(self.style.HTTP_INFO('ℹ For trusted certificates, install mkcert'))

        try:
            # Generate private key
            self.stdout.write(self.style.HTTP_INFO('ℹ Generating private key...'))
            subprocess.run([
                'openssl', 'genrsa',
                '-out', str(self.key_file),
                '2048'
            ], check=True, capture_output=True)

            # Generate certificate
            self.stdout.write(self.style.HTTP_INFO('ℹ Generating certificate...'))
            subprocess.run([
                'openssl', 'req', '-new', '-x509',
                '-key', str(self.key_file),
                '-out', str(self.cert_file),
                '-days', '365',
                '-subj', '/C=US/ST=State/L=City/O=Development/CN=localhost',
                '-addext', 'subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1,IP:::1'
            ], check=True, capture_output=True)

            self.stdout.write(self.style.SUCCESS('✓ Self-signed certificates generated with OpenSSL!'))
            self.stdout.write(self.style.WARNING('⚠ You\'ll need to manually trust these certificates'))
            self.cert_method = 'openssl'

        except subprocess.CalledProcessError as e:
            raise CommandError(f'Failed to generate certificates with OpenSSL: {e}')

        # Set proper permissions (Unix-like systems only)
        if os.name != 'nt':  # Not Windows
            os.chmod(self.key_file, 0o600)
            os.chmod(self.cert_file, 0o644)

    def print_completion(self):
        """Print completion message with next steps"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════════════════'))
        if hasattr(self, 'cert_method') and self.cert_method == 'mkcert':
            self.stdout.write(self.style.SUCCESS('SSL Setup Complete with mkcert! 🎉'))
        else:
            self.stdout.write(self.style.SUCCESS('SSL Setup Complete!'))
        self.stdout.write(self.style.SUCCESS('═══════════════════════════════════════════════════'))
        self.stdout.write('')

        self.stdout.write(self.style.HTTP_INFO(f'Certificate: {self.cert_file}'))
        self.stdout.write(self.style.HTTP_INFO(f'Key: {self.key_file}'))
        self.stdout.write('')

        self.stdout.write(self.style.NOTICE('Next steps:'))
        self.stdout.write(f'  1. Run: python manage.py runsslserver --certificate {self.cert_file} --key {self.key_file}')
        self.stdout.write('  2. Visit: https://127.0.0.1:8000')

        if hasattr(self, 'cert_method') and self.cert_method == 'mkcert':
            self.stdout.write('  3. You should see a secure connection (no warnings)! ✓')
        else:
            self.stdout.write('  3. Accept the security warning in your browser')

        self.stdout.write('')
