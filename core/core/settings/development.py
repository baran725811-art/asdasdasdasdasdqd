#core\core\settings\development.py
from .base import *

DEBUG = True
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-only-for-local-dev')
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# E-posta ayarları (console backend - geliştirme için)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Debug Toolbar Konfigürasyonu
if DEBUG:
    # Debug toolbar'ı INSTALLED_APPS'e ekle
    INSTALLED_APPS += ['debug_toolbar']
    # Debug toolbar middleware'ini en başa ekle (performans izleme için)
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

    # Internal IPs - Debug toolbar'ın çalışması için
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
        '[::1]',  # IPv6 localhost
    ] 

    # Debug Toolbar ayarları
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_COLLAPSED': False,
        'INTERCEPT_REDIRECTS': False,
    }