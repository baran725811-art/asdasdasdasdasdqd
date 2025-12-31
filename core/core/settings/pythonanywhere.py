# core/settings/pythonanywhere.py - PythonAnywhere Ücretsiz Deployment Ayarları

from .base import *
from decouple import config
import os

# PYTHONEANYWHERE DEPLOYMENT AYARLARI
# =====================================
# Bu dosya PythonAnywhere ücretsiz hesabı için optimize edilmiştir

# Production güvenlik ayarları
DEBUG = False
SECRET_KEY = config('SECRET_KEY')

# PythonAnywhere host ayarları
# yourname.pythonanywhere.com formatında
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# CSRF trusted origins - PythonAnywhere domain'i
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS',
                             cast=lambda v: [s.strip() for s in v.split(',')])

# =====================================
# DATABASE - MYSQL (PythonAnywhere Free)
# =====================================
# PythonAnywhere ücretsiz hesapta MySQL kullanılır
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),          # yourname$dbname
        'USER': config('DB_USER'),          # yourname
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='yourname.mysql.pythonanywhere-services.com'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 300,  # 5 dakika connection pooling
    }
}

# =====================================
# CACHE - FILE BASED (Redis yok)
# =====================================
# PythonAnywhere ücretsiz hesapta Redis yok, file-based cache kullanıyoruz
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 3600,  # 1 saat
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 3,
        },
        'KEY_PREFIX': 'baran_anahtarci',
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# =====================================
# HTTPS/SSL AYARLARI
# =====================================
# PythonAnywhere otomatik HTTPS sağlar
SECURE_SSL_REDIRECT = False  # PythonAnywhere otomatik handle eder
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookie güvenliği
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# HSTS ayarları - daha sonra aktif edilebilir
SECURE_HSTS_SECONDS = 0  # İlk deployment'ta kapalı
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# =====================================
# STATIC & MEDIA FILES
# =====================================
# PythonAnywhere için static files ayarları
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'static')  # /home/username/static/

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')  # /home/username/media/

# Static files storage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Media files - Cloudinary (ücretsiz tier)
if config('USE_CLOUDINARY', default=True, cast=bool):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# =====================================
# LOGGING - HOME DIRECTORY
# =====================================
# PythonAnywhere'de /var/log/ yetkisi yok, home dizini kullanıyoruz
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

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
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB (ücretsiz hesap için küçük)
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'security.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 3,
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'console'],
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

# =====================================
# EMAIL AYARLARI
# =====================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@example.com')

# Admin notifications
ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='admin@example.com')),
]
MANAGERS = ADMINS

# =====================================
# SECURITY MONITORING
# =====================================
SECURITY_MONITORING = {
    'LOG_FAILED_LOGINS': True,
    'LOG_SUSPICIOUS_REQUESTS': True,
    'BLOCK_SUSPICIOUS_IPS': True,
    'MAX_LOGIN_ATTEMPTS': 3,
    'LOGIN_ATTEMPT_TIMEOUT': 600,  # 10 dakika
}

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# =====================================
# MIDDLEWARE - Production
# =====================================
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
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

# =====================================
# TEMPLATE CACHING
# =====================================
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# =====================================
# COMPRESSION
# =====================================
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

# =====================================
# ADMIN PANEL
# =====================================
ADMIN_URL = config('ADMIN_URL', default='secure-admin-panel/')

# =====================================
# FILE UPLOAD LIMITS
# =====================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# =====================================
# PYTHONANYWHERE SPECIFIC
# =====================================
# PythonAnywhere için özel ayarlar
PYTHONANYWHERE_DOMAIN = config('PYTHONANYWHERE_DOMAIN', default='yourname.pythonanywhere.com')

# Cache middleware timeout
CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_KEY_PREFIX = 'baran_anahtarci'

print("""
✓ PythonAnywhere ayarları yüklendi
✓ MySQL veritabanı kullanılıyor
✓ File-based cache kullanılıyor
✓ Log dosyaları: {log_dir}
✓ Static files: {static_root}
""".format(log_dir=LOG_DIR, static_root=STATIC_ROOT))
