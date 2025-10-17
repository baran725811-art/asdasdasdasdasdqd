# core/management/commands/security_check.py - YENİ DOSYA OLUŞTUR

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
import os
import stat

class Command(BaseCommand):
    help = 'Django projesi güvenlik kontrolü yapar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Güvenlik sorunlarını otomatik düzelt',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Güvenlik kontrolü başlatılıyor...'))
        
        issues = []
        
        # 1. DEBUG kontrolü
        if getattr(settings, 'DEBUG', True):
            issues.append('CRITICAL: DEBUG=True production ortamında kapatılmalı')
        
        # 2. SECRET_KEY kontrolü
        secret_key = getattr(settings, 'SECRET_KEY', '')
        if len(secret_key) < 50:
            issues.append('HIGH: SECRET_KEY çok kısa, en az 50 karakter olmalı')
        
        # 3. ALLOWED_HOSTS kontrolü
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        if '*' in allowed_hosts and not settings.DEBUG:
            issues.append('HIGH: ALLOWED_HOSTS production\'da \'*\' içermemeli')
        
        # 4. HTTPS ayarları kontrolü
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False) and not settings.DEBUG:
            issues.append('MEDIUM: SECURE_SSL_REDIRECT production\'da True olmalı')
        
        # 5. HSTS kontrolü
        hsts_seconds = getattr(settings, 'SECURE_HSTS_SECONDS', 0)
        if hsts_seconds == 0 and not settings.DEBUG:
            issues.append('MEDIUM: SECURE_HSTS_SECONDS ayarlanmalı')
        
        # 6. Cookie güvenliği
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False) and not settings.DEBUG:
            issues.append('MEDIUM: SESSION_COOKIE_SECURE True olmalı')
        
        # 7. Admin kullanıcı kontrolü
        weak_passwords = self._check_weak_passwords()
        if weak_passwords:
            issues.extend(weak_passwords)
        
        # 8. Dosya izinleri kontrolü
        file_issues = self._check_file_permissions()
        if file_issues:
            issues.extend(file_issues)
        
        # 9. Middleware kontrolü
        security_middlewares = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
        
        middleware = getattr(settings, 'MIDDLEWARE', [])
        for mw in security_middlewares:
            if mw not in middleware:
                issues.append(f'MEDIUM: {mw} middleware eksik')
        
        # Sonuçları göster
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ Güvenlik kontrolü tamamlandı - sorun bulunamadı'))
        else:
            self.stdout.write(self.style.ERROR(f'⚠️  {len(issues)} güvenlik sorunu bulundu:'))
            for issue in issues:
                level = issue.split(':')[0]
                message = ':'.join(issue.split(':')[1:])
                
                if level == 'CRITICAL':
                    self.stdout.write(self.style.ERROR(f'🔴 {issue}'))
                elif level == 'HIGH':
                    self.stdout.write(self.style.WARNING(f'🟠 {issue}'))
                else:
                    self.stdout.write(self.style.HTTP_INFO(f'🟡 {issue}'))
        
        # Otomatik düzeltme
        if options['fix']:
            self._apply_fixes()

    def _check_weak_passwords(self):
        """Zayıf admin parolalarını kontrol et"""
        issues = []
        try:
            superusers = User.objects.filter(is_superuser=True)
            for user in superusers:
                if user.check_password('admin') or user.check_password('password'):
                    issues.append(f'CRITICAL: {user.username} zayıf parola kullanıyor')
        except:
            pass
        return issues

    def _check_file_permissions(self):
        """Kritik dosya izinlerini kontrol et"""
        issues = []
        
        critical_files = [
            '.env',
            'db.sqlite3',
            'logs/',
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                file_stat = os.stat(file_path)
                mode = stat.filemode(file_stat.st_mode)
                
                # 644'ten daha açık izinler varsa uyar
                if file_stat.st_mode & 0o077:  # Group/other write permissions
                    issues.append(f'MEDIUM: {file_path} dosya izinleri güvensiz ({mode})')
        
        return issues

    def _apply_fixes(self):
        """Bazı güvenlik sorunlarını otomatik düzelt"""
        self.stdout.write(self.style.SUCCESS('🔧 Otomatik düzeltmeler uygulanıyor...'))
        
        # Dosya izinlerini düzelt
        critical_files = ['.env', 'db.sqlite3']
        for file_path in critical_files:
            if os.path.exists(file_path):
                os.chmod(file_path, 0o600)
                self.stdout.write(f'✅ {file_path} izinleri düzeltildi')
        
        # Log klasörü izinlerini düzelt
        if os.path.exists('logs/'):
            os.chmod('logs/', 0o755)
            for root, dirs, files in os.walk('logs/'):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
            self.stdout.write('✅ Log klasörü izinleri düzeltildi')