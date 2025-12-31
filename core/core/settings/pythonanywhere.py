# core/settings/pythonanywhere.py - PythonAnywhere FREE TIER SETTINGS

from .base import *
from decouple import config

# ========================
# PYTHONANYWHERE BASIC SETTINGS
# ========================

# Debug - PythonAnywhere'de False olmalı
DEBUG = config('DEBUG', default=False, cast=bool)

# Secret Key
SECRET_KEY = config('SECRET_KEY', default='pythonanywhere-temporary-key-CHANGE-THIS-IN-ENV-FILE!')

# Allowed Hosts - PythonAnywhere domain
# Format: username.pythonanywhere.com
ALLOWED_HOSTS = config('ALLOWED_HOSTS',
                       default='localhost,127.0.0.1,.pythonanywhere.com',
                       cast=lambda v: [s.strip() for s in v.split(',')])

# ========================
# DATABASE - SQLite (FREE TIER)
# ========================

# PythonAnywhere ücretsiz hesapta SQLite kullanıyoruz
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# ========================
# CACHE - FILE BASED (FREE TIER)
# ========================

# Redis yok, file-based cache kullanıyoruz
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 3600,
        'OPTIONS': {
            'MAX_ENTRIES': 5000,
            'CULL_FREQUENCY': 3,
        },
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# ========================
# SECURITY SETTINGS (SIMPLIFIED)
# ========================

# PythonAnywhere HTTP olarak çalışır, HTTPS redirect kapalı
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# HSTS devre dışı (ücretsiz tier için)
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS',
                             default='https://*.pythonanywhere.com',
                             cast=lambda v: [s.strip() for s in v.split(',')])

# ========================
# STATIC FILES
# ========================

# PythonAnywhere için static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Static files storage - basit
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ========================
# MEDIA FILES
# ========================

# Cloudinary kullanıyorsanız (önerilir)
if config('CLOUDINARY_CLOUD_NAME', default=None):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': config('CLOUDINARY_API_KEY'),
        'API_SECRET': config('CLOUDINARY_API_SECRET'),
    }
else:
    # Yoksa local media storage
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========================
# LOGGING - SIMPLIFIED
# ========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'simple',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ========================
# MIDDLEWARE - SIMPLIFIED
# ========================

# Production middleware'lerden bazılarını kaldırıyoruz (ücretsiz tier için)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Sadece temel middleware'ler
]

# ========================
# EMAIL - Console Backend (Test için)
# ========================

# Email ayarları - production'da SMTP kullanın
EMAIL_BACKEND = config('EMAIL_BACKEND',
                      default='django.core.mail.backends.console.EmailBackend')

# ========================
# COMPRESSION - DISABLED
# ========================

# Ücretsiz tier için compression kapalı
COMPRESS_ENABLED = False

# ========================
# TEMPLATE CACHING - ENABLED
# ========================

# Template caching - performans için
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# ========================
# ADMIN URL
# ========================

ADMIN_URL = config('ADMIN_URL', default='admin/')

# ========================
# PYTHONANYWHERE SPECIFIC
# ========================

# File upload limits (ücretsiz tier için düşük)
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Security monitoring - basit
SECURITY_MONITORING = {
    'LOG_FAILED_LOGINS': False,
    'LOG_SUSPICIOUS_REQUESTS': False,
    'BLOCK_SUSPICIOUS_IPS': False,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOGIN_ATTEMPT_TIMEOUT': 300,
}

# Rate limiting - devre dışı (ücretsiz tier için)
RATELIMIT_ENABLE = False

print("🐍 PythonAnywhere settings loaded (Free Tier)")
