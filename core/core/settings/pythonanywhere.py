# core/settings/pythonanywhere.py
# PythonAnywhere için özel production ayarları

from .production import *
from decouple import config
import os

# PythonAnywhere özel ayarlar
DEBUG = False

# Database - PythonAnywhere için esnek yapılandırma
# PostgreSQL varsa kullan, yoksa SQLite fallback
USE_POSTGRES = config('USE_POSTGRES', default=False, cast=bool)

if USE_POSTGRES:
    # PostgreSQL configuration (Ücretli plan)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': config('DB_SSL_MODE', default='prefer'),
            },
            'CONN_MAX_AGE': 600,
        }
    }
else:
    # SQLite configuration (Ücretsiz plan)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Cache - PythonAnywhere ücretsiz planda Redis yok, file-based cache kullan
USE_REDIS = config('USE_REDIS', default=False, cast=bool)

if USE_REDIS:
    # Redis cache (Ücretli plan)
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'baran_anahtarci',
            'TIMEOUT': 3600,
        }
    }
else:
    # File-based cache (Ücretsiz plan)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': BASE_DIR / 'cache',
            'TIMEOUT': 3600,
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    }

# Session - Cache yerine database kullan (SQLite ile uyumlu)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Static files - PythonAnywhere özel
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Media files - Cloudinary kullanıyoruz (ücretsiz/ücretli her ikisinde de çalışır)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Logging - PythonAnywhere için basitleştirilmiş
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
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 3,
            'formatter': 'simple',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Security ayarları - PythonAnywhere HTTPS'i otomatik sağlar
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# PythonAnywhere subdomain için HSTS'i biraz daha yumuşat
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

# Cloudinary - PythonAnywhere'de sorunsuz çalışır
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Email - PythonAnywhere'den email gönderimi
# Gmail App Password kullanmanız önerilir
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# PythonAnywhere API whitelist kontrolü
# Ücretsiz hesaplarda sadece whitelist'teki API'lere istek yapılabilir
# DeepL API whitelisted, Cloudinary da whitelisted

# Admin URL güvenliği
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Axes - Brute force protection
AXES_ENABLED = True
AXES_FAILURE_LIMIT = config('MAX_LOGIN_ATTEMPTS', default=3, cast=int)
AXES_COOLOFF_TIME = config('LOGIN_ATTEMPT_TIMEOUT', default=10, cast=int)  # dakika cinsinden
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True

# Debug toolbar'ı devre dışı bırak (production)
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Güvenlik middleware'ları aktif
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.SecurityMonitoringMiddleware',
    'core.middleware.LoginSecurityMiddleware',
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

# PythonAnywhere performans optimizasyonları
CONN_MAX_AGE = 600 if USE_POSTGRES else 0

# Template rendering optimizasyonu
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

print("⚙️ PythonAnywhere Production Settings Loaded")
print(f"   Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
print(f"   Cache: {'Redis' if USE_REDIS else 'File-based'}")
print(f"   Debug: {DEBUG}")
