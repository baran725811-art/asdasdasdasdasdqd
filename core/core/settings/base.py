# core/settings/base.py
from pathlib import Path
import os
from decouple import config
from django.utils.translation import gettext_lazy as _
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# BU SATIRLARI EKLE:
DEBUG = config('DEBUG', default=True, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-this-in-production-minimum-50-characters-long!')
ALLOWED_HOSTS = ['*']  # Development için

# Database ayarını da ekle (eksik olan)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # Core apps
    'core',
    'home',
    'products',
    'gallery',
    'about',
    'contact',
    'dashboard',
    'reviews',

    # Third party apps - Security packages
    'axes',           # Rate limiting ve brute force koruması
    'captcha',        # CAPTCHA koruması

    # Other third party apps
    'imagekit',
    'django_ckeditor_5',
    'widget_tweaks',
    'modeltranslation',
    'cloudinary_storage',
    'cloudinary',
    'compressor',
]
# Security middleware sıralaması - EN ÖNEMLİ DEĞİŞİKLİK
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',  # En başta
    'core.middleware.SecurityHeadersMiddleware',      # Özel güvenlik middleware'i
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

# Güçlü password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # 8'den 12'ye çıkarıldı
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'core.validators.CustomPasswordValidator',  # Mevcut validator'ınızı ekleyin
    },
]

# Güvenli password hashers - en güvenli olanlar başta
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Rate limiting ayarları - gelişmiş
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_VIEW = 'core.views.ratelimit_view'


# Admin güvenliği
ADMIN_URL = config('ADMIN_URL', default='admin/')  # Özelleştirilebilir admin URL
ADMIN_SESSION_TIMEOUT = 60 * 30  # 30 dakika


# Logging - güvenlik olayları için gelişmiş
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': 'SECURITY {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core.security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Security monitoring
SECURITY_MONITORING = {
    'LOG_FAILED_LOGINS': True,
    'LOG_SUSPICIOUS_REQUESTS': True,
    'BLOCK_SUSPICIOUS_IPS': True,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOGIN_ATTEMPT_TIMEOUT': 300,  # 5 dakika
}







ROOT_URLCONF = 'core.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'core.context_processors.seo_context',
                'core.context_processors.meta_seo_context',  # Meta SEO context
                'core.context_processors.breadcrumb_context',  # Breadcrumb context
                'core.context_processors.language_context',
                'core.context_processors.storage_info',
            ],
        },
    },
]  
# Database
# Bu kısım development.py veya production.py'de tanımlanmalı
# Cache Configuration
"""CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'site-cache',
        'TIMEOUT': 900,  # 15 dakika
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        },
        'KEY_PREFIX': 'site_cache',
        'VERSION': 1,
    }
}"""
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
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
    
COMPRESS_ENABLED = config('COMPRESS_ENABLED', default=not DEBUG, cast=bool)

# Cache için session ayarları
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
# Statik dosyalar (CSS, JS, resimler)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Geliştirme aşaması için
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')    # collectstatic çıktısı
# Medya dosyaları (kullanıcı yüklemeleri)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Internationalization (Çoklu dil desteği)
LANGUAGE_CODE = 'tr'  # Varsayılan dil Türkçe
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True
# Desteklenen diller
# Mevcut LANGUAGES ayarını şu şekilde değiştir:
LANGUAGES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('ar', 'العربية'),
    ('ru', 'Русский'),
]
# Dil dosyalarının konumu
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
# Dashboard için özel dil ayarları
DASHBOARD_LANGUAGES = [
    ('tr', _('Türkçe')),
    ('en', _('English')),
    ('de', _('Deutsch')),
    ('fr', _('Français')),
    ('es', _('Español')),
    ('ru', _('Русский')),
    ('ar', _('العربية')),
]
# Dil algılama ayarları
LANGUAGE_SESSION_KEY = 'django_language'
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 yıl
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SECURE = False  # Production'da True olacak
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = 'Lax'
# Dashboard dil cookie ayarları
DASHBOARD_LANGUAGE_COOKIE_NAME = 'dashboard_language'
DASHBOARD_LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 yıl
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# File upload ayarları
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB


# SSL/HTTPS ayarları - production/development'a göre dinamik
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if not DEBUG else None
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)

# HSTS (HTTP Strict Transport Security) ayarları
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0 if DEBUG else 31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not DEBUG, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=not DEBUG, cast=bool)

# CSRF koruması - gelişmiş ayarlar
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = False  # Cookie tabanlı CSRF
CSRF_COOKIE_AGE = 31449600  # 1 yıl
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', 
                             default='http://localhost:8000,http://127.0.0.1:8000', 
                             cast=lambda v: [s.strip() for s in v.split(',')])

# Session güvenliği
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 hafta
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

# XSS ve güvenlik koruması
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# Content Security Policy (CSP) ayarları
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "'unsafe-eval'", 
                  "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net",
                  "https://res.cloudinary.com"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", 
                 "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com"]
CSP_IMG_SRC = ["'self'", "data:", "https:", "https://res.cloudinary.com"]
CSP_FONT_SRC = ["'self'", "https://fonts.gstatic.com"]
CSP_CONNECT_SRC = ["'self'", "https://api.cloudinary.com"]
CSP_FRAME_SRC = ["'none'"]
CSP_OBJECT_SRC = ["'none'"]
CSP_MEDIA_SRC = ["'self'", "https://res.cloudinary.com"]


# Güvenli dosya yükleme
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Güvenli allowed hosts
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# Static files storage - production'da optimize
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# CKEditor ayarları
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        'height': 200,
        'width': '100%',
    },
}
# Modeltranslation ayarları
MODELTRANSLATION_DEFAULT_LANGUAGE = 'tr'
MODELTRANSLATION_LANGUAGES = ('tr', 'en', 'fr', 'de', 'ar', 'ru')
MODELTRANSLATION_FALLBACK_LANGUAGES = ('tr', 'en')
# DeepL API ayarları
DEEPL_API_URL = 'https://api-free.deepl.com/v2/translate'  # Free plan için
# DEEPL_API_URL = 'https://api.deepl.com/v2/translate'  # Pro plan için
DEEPL_CHARACTER_LIMIT = 500000  # Müşteri başına karakter limiti




# ========================
# ERROR HANDLERS (SEO)
# ========================

# Custom error handler views
HANDLER404 = 'core.views.custom_404_view'
HANDLER500 = 'core.views.custom_500_view'
HANDLER403 = 'core.views.custom_403_view'
HANDLER400 = 'core.views.custom_400_view'

# Error page settings
ERROR_PAGE_SETTINGS = {
    'SHOW_SEARCH_ON_404': True,
    'SHOW_SUGGESTIONS_ON_404': True,
    'MAX_SUGGESTIONS': 6,
    'SUGGESTION_CACHE_TIMEOUT': 3600,  # 1 saat
    'LOG_404_ERRORS': True,
    'LOG_500_ERRORS': True,
    'MAINTENANCE_MODE': False,
}

# 404 Error tracking
TRACK_404_ERRORS = True
MAX_404_LOGS_PER_IP = 10  # IP başına maksimum 404 log sayısı

# Broken link monitoring
BROKEN_LINK_MONITORING = {
    'ENABLED': True,
    'ALERT_THRESHOLD': 5,  # 5 broken link'te uyarı
    'CHECK_INTERVAL': 24,  # 24 saatte bir kontrol
    'EXCLUDE_PATTERNS': [
        r'^/admin/',
        r'^/dashboard/',
        r'^/api/',
        r'\.css$',
        r'\.js$',
        r'\.ico$',
    ],
}

# Maintenance mode ayarları
MAINTENANCE_MODE_SETTINGS = {
    'ENABLED': False,
    'ALLOWED_IPS': ['127.0.0.1'],  # Bakım sırasında erişebilecek IP'ler
    'MESSAGE': 'Site bakım modunda. Kısa süre sonra tekrar açılacaktır.',
    'ESTIMATED_TIME': '30 dakika',
}

# SEO Error page meta
ERROR_PAGE_META = {
    '404': {
        'title': 'Sayfa Bulunamadı - 404',
        'description': 'Aradığınız sayfa bulunamadı. Popüler ürünlerimizi ve içeriklerimizi keşfedin.',
        'robots': 'noindex, follow',
    },
    '500': {
        'title': 'Sunucu Hatası - 500',
        'description': 'Geçici sunucu hatası. Yakında normale dönecektir.',
        'robots': 'noindex, nofollow',
    },
    '403': {
        'title': 'Erişim Reddedildi - 403',
        'description': 'Bu sayfaya erişim izniniz bulunmuyor.',
        'robots': 'noindex, nofollow',
    },
    '400': {
        'title': 'Hatalı İstek - 400',
        'description': 'Hatalı istek gönderildi.',
        'robots': 'noindex, nofollow',
    },
}