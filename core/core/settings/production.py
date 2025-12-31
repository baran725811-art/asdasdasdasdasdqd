#core\core\settings\production.py
# core/settings/production.py - PRODUCTION GÜVENLIK AYARLARI

from .base import *
from decouple import config

# Production güvenlik ayarları
DEBUG = False
SECRET_KEY = config('SECRET_KEY')

# Güvenli host ayarları
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# HTTPS zorunlu ayarları
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie güvenliği
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# CSRF trusted origins - production domain'leri
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', 
                             cast=lambda v: [s.strip() for s in v.split(',')])

# Security middleware - production için SecurityMonitoringMiddleware ekle
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.SecurityMonitoringMiddleware',  # Production'da aktif
    'core.middleware.LoginSecurityMiddleware',       # Production'da aktif
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'core.middleware.SEOCanonicalMiddleware',
    'core.middleware.URLRedirectMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
    'core.middleware.IPAddressMiddleware',
    'core.middleware.SitePrimaryLanguageMiddleware',
    'core.middleware.DashboardLocaleMiddleware',
]

# Database - production için optimize
# PythonAnywhere için: SQLite veya MySQL kullanabilirsiniz
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    # SQLite - küçük projeler için
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif DB_ENGINE == 'django.db.backends.mysql':
    # MySQL - PythonAnywhere için önerilir
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
            'CONN_MAX_AGE': 600,
        }
    }
else:
    # PostgreSQL - kendi sunucunuz için
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'require',
            },
            'CONN_MAX_AGE': 600,
        }
    }

# Cache - production için
# PythonAnywhere ücretsiz hesaplarda Redis yok, file-based cache kullanın
CACHE_BACKEND = config('CACHE_BACKEND', default='django.core.cache.backends.filebased.FileBasedCache')

if CACHE_BACKEND == 'django_redis.cache.RedisCache':
    # Redis - kendi sunucunuz veya paid plan için
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'ssl_cert_reqs': None,
                },
            },
            'KEY_PREFIX': 'baran_anahtarci_prod',
            'TIMEOUT': 3600,
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # File-based cache - PythonAnywhere için
    import os
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.join(BASE_DIR, 'cache'),
            'TIMEOUT': 3600,
            'OPTIONS': {
                'MAX_ENTRIES': 10000,
                'CULL_FREQUENCY': 3,
            },
        }
    }
    # File-based cache ile cached_db session engine kullan
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    SESSION_CACHE_ALIAS = 'default'

# Logging - production için kapsamlı
# PythonAnywhere için logs dizini proje içinde
import os
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': 'SECURITY {asctime} [{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'security',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email ayarları - production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Admin notifications
ADMINS = [
    ('Admin', config('ADMIN_EMAIL')),
]
MANAGERS = ADMINS

# Güvenlik monitoring - production ayarları
SECURITY_MONITORING = {
    'LOG_FAILED_LOGINS': True,
    'LOG_SUSPICIOUS_REQUESTS': True,
    'BLOCK_SUSPICIOUS_IPS': True,
    'MAX_LOGIN_ATTEMPTS': 3,  # Production'da daha sıkı
    'LOGIN_ATTEMPT_TIMEOUT': 600,  # 10 dakika
}

# Rate limiting - production için sıkı
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Static files - production için optimized
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
# PythonAnywhere için static root
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files - Cloudinary için production ayarları
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Template caching - production için aktif
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Cache ayarları - production için optimize
CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_KEY_PREFIX = 'baran_anahtarci_prod'

# Compression - production için aktif
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

# Admin URL güvenliği
ADMIN_URL = config('ADMIN_URL', default='secure-admin-panel/')

# File upload limits - production için sıkı
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB