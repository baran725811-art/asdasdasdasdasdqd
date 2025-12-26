#core\core\settings.py
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# SSL/HTTPS ayarları (development için devre dışı)
SECURE_SSL_REDIRECT = False if DEBUG else True
SECURE_PROXY_SSL_HEADER = None if DEBUG else ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG


# CSRF koruması
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'  # Bu satırı ekleyin
CSRF_FAILURE_VIEW = 'core.views.csrf_failure_view'  # Bu satırı ekleyin
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost,http://127.0.0.1', 
                             cast=lambda v: [s.strip() for s in v.split(',')])

# XSS ve güvenlik koruması
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy ayarları - Production için
if not DEBUG:
    CSP_DEFAULT_SRC = ["'self'"]
    CSP_SCRIPT_SRC = [
        "'self'", 
        "'unsafe-inline'",  # CKEditor için gerekli
        "'unsafe-eval'",    # Chart.js için gerekli
        "https://cdnjs.cloudflare.com",
        "https://res.cloudinary.com"
    ]
    CSP_STYLE_SRC = [
        "'self'", 
        "'unsafe-inline'",
        "https://fonts.googleapis.com"
    ]
    CSP_IMG_SRC = ["'self'", "data:", "https:", "https://res.cloudinary.com"]
    CSP_FONT_SRC = ["'self'", "https://fonts.gstatic.com"]
    CSP_CONNECT_SRC = ["'self'", "https://api.cloudinary.com"]
    CSP_FRAME_SRC = ["'none'"]
    CSP_OBJECT_SRC = ["'none'"]
    CSP_MEDIA_SRC = ["'self'", "https://res.cloudinary.com"]



# Password hashing - en güvenli hashers
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# Application definition
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
    
    # Third party apps - GÜVENLİK PAKETLERİ EKLENDİ
    'axes',           # Rate limiting ve brute force koruması
    'captcha',        # CAPTCHA koruması
    
    # Diğer third party apps
    'imagekit',
    'django_ckeditor_5',
    'widget_tweaks',
    'modeltranslation',
    'cloudinary_storage',
    'cloudinary',
    'compressor',
]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    
    # SEO Middleware
    'core.middleware.SEOCanonicalMiddleware',
    'core.middleware.URLRedirectMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
    
    # GÜVENLİK MIDDLEWARE EKLENDİ
    'axes.middleware.AxesMiddleware',  # En sona eklendi
    
    # Custom middleware
    'core.middleware.IPAddressMiddleware',
    'core.middleware.SitePrimaryLanguageMiddleware',
    'core.middleware.DashboardLocaleMiddleware',
]

# Debug toolbar (sadece development)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG and not request.path.startswith('/dashboard/'),
        'HIDE_DJANGO_SQL': False,
        'INTERCEPT_REDIRECTS': False,
        'INSERT_BEFORE': '</body>',
        'RESULTS_CACHE_SIZE': 10,
    }
    
    
# AXES CONFIGURATION - TÜM AYARLARI DEĞİŞTİRİN
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 saat
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'errors/lockout.html'
AXES_ENABLE_ADMIN = True

AXES_LOCKOUT_PARAMETERS = ['ip_address', 'username']

# CAPTCHA CONFIGURATION
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'  # Matematik soruları
CAPTCHA_MATH_CHALLENGE_OPERATOR = '+'  # Sadece toplama işlemi
CAPTCHA_LENGTH = 6  # Kod uzunluğu
CAPTCHA_TIMEOUT = 5  # 5 dakika geçerlilik süresi
CAPTCHA_IMAGE_SIZE = (120, 50)  # Görüntü boyutu
CAPTCHA_BACKGROUND_COLOR = '#f8f9fa'  # Arka plan rengi
CAPTCHA_FOREGROUND_COLOR = '#495057'  # Yazı rengi
CAPTCHA_FONT_SIZE = 22  # Font boyutu
CAPTCHA_LETTER_ROTATION = (-5, 5)  # Harf rotasyonu (azaltıldı)
CAPTCHA_NOISE_FUNCTIONS = (
    'captcha.helpers.noise_arcs',
    'captcha.helpers.noise_dots',
)

# Rate limiting - mevcut ayarları koruyun
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_VIEW = 'core.views.ratelimit_view'

ROOT_URLCONF = 'core.urls'

# TEMPLATE CONFIGURATION
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
                'core.context_processors.meta_seo_context',
                'core.context_processors.footer_context',
                'dashboard.context_processors.notification_context', 
                'core.context_processors.storage_info',
            ],
        },
    },
]

# Template caching for production
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

WSGI_APPLICATION = 'core.wsgi.application'

# DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            'check_same_thread': False,
        },
        'TEST': {
            'NAME': ':memory:'
        }
    }
}

# CACHE CONFIGURATION
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
        'VERSION': 1,
    },
    'template_cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache', 'templates'),
        'TIMEOUT': 7200,  # 2 saat
    },
    'database_cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache', 'database'),
        'TIMEOUT': 1800,  # 30 dakika
    }
}

# DEBUG modunda cache'i kapat
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Cache middleware settings
CACHE_MIDDLEWARE_SECONDS = 3600 if not DEBUG else 0
CACHE_MIDDLEWARE_KEY_PREFIX = 'baran_anahtarci'
CACHE_MIDDLEWARE_ALIAS = 'default'

# SESSION OPTIMIZATION
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 hafta
SESSION_SAVE_EVERY_REQUEST = False  # Performans için

# Login URLs
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/dashboard/login/'
LOGOUT_URL = '/dashboard/logout/'

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # 8 - GÜÇLÜ ŞİFRE
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'core.validators.CustomPasswordValidator',  # ÖZELLEŞTİRİLMİŞ VALIDATOR
    },
]

# AUTHENTICATION BACKENDS - AXES İÇİN GEREKLİ
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # Axes backend ekledik
    'django.contrib.auth.backends.ModelBackend',  # Default backend
]

# INTERNATIONALIZATION
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported languages
LANGUAGES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('es', 'Español'),
    ('ru', 'Русский'),
    ('ar', 'العربية'),
]

# Locale paths
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# STATIC FILES CONFIGURATION
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # BU SATIRI EKLEYİN
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
] 

# Static files optimization
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# CSS/JS COMPRESSION
COMPRESS_ENABLED = not DEBUG
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
COMPRESS_OFFLINE = not DEBUG
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_JS_HASHING_METHOD = 'content'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='your-email@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='your-app-password')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='your-email@gmail.com')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='your-email@gmail.com')
EMAIL_TIMEOUT = 10

# CKEDITOR CONFIGURATION
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': [
                'heading', '|',
                'bold', 'italic', 'underline', '|',
                'bulletedList', 'numberedList', '|',
                'outdent', 'indent', '|',
                'blockQuote', 'link', '|',
                'insertTable', '|',
                'undo', 'redo'
            ]
        },
        'height': '400px',
        'language': 'tr',
        'placeholder': 'İçeriği buraya yazın...',
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraf', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Başlık 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Başlık 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Başlık 3', 'class': 'ck-heading_heading3'},
            ]
        },
        'link': {
            'addTargetToExternalLinks': True,
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells'
            ]
        }
    },
    'minimal': {
        'toolbar': {
            'items': ['bold', 'italic', '|', 'link', 'bulletedList', 'numberedList']
        },
        'height': '200px',
        'language': 'tr',
    },
}

# CKEditor upload settings
CKEDITOR_5_UPLOAD_PATH = "uploads/"
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.DefaultStorage"
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'tiff']
CKEDITOR_5_MAX_FILE_SIZE = 5242880  # 5MB

# CLOUDINARY CONFIGURATION
import cloudinary
import cloudinary.uploader
import cloudinary.api

STORAGE_INFO_ADMIN_ONLY = not DEBUG

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
    'SECURE': True,
}

# Cloudinary storage packages
CLOUDINARY_STORAGE_PACKAGES = {
    5: 5 * 1024 * 1024 * 1024,
    10: 10 * 1024 * 1024 * 1024,
    15: 15 * 1024 * 1024 * 1024,
    20: 20 * 1024 * 1024 * 1024,
    25: 25 * 1024 * 1024 * 1024,
}

CLOUDINARY_STORAGE_LIMIT_GB = int(config('CLOUDINARY_STORAGE_LIMIT', default='5'))
CLOUDINARY_STORAGE_LIMIT_BYTES = CLOUDINARY_STORAGE_PACKAGES.get(
    CLOUDINARY_STORAGE_LIMIT_GB, 
    CLOUDINARY_STORAGE_PACKAGES[5]
)

# Cloudinary config
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=CLOUDINARY_STORAGE['SECURE']
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_URL_PREFIX = f"https://res.cloudinary.com/{CLOUDINARY_STORAGE['CLOUD_NAME']}/"

# Cloudinary storage limits
CLOUDINARY_STORAGE.update({
    'STORAGE_LIMIT': CLOUDINARY_STORAGE_LIMIT_BYTES,
    'STORAGE_LIMIT_GB': CLOUDINARY_STORAGE_LIMIT_GB,
    'MAX_FILE_SIZE': 100 * 1024 * 1024,  # 100MB
    'MAX_IMAGE_SIZE': 20 * 1024 * 1024,  # 20MB
    'MAX_VIDEO_SIZE': 100 * 1024 * 1024,  # 100MB
})

# görsel boyutları
CLOUDINARY_DEFAULT_TRANSFORMATIONS = {
    'image': {
        'quality': 'auto:eco',  # Aggressive compression
        'fetch_format': 'auto',  # WebP/AVIF automatic
        'width': 1920,
        'height': 1080,
        'crop': 'limit',
        'progressive': True,  # Progressive JPEG
        'strip': True,  # Remove EXIF data
    },
    'thumbnail': {
        'quality': 'auto:good',
        'fetch_format': 'auto',
        'width': 400,
        'height': 300,
        'crop': 'fill',
        'gravity': 'auto',
        'strip': True,
    },
    'gallery': {
        'quality': 'auto:good',
        'fetch_format': 'auto',
        'width': 800,
        'height': 600,
        'crop': 'limit',
        'progressive': True,
        'strip': True,
    },
    'carousel': {
        'quality': 'auto:good',
        'fetch_format': 'auto',
        'width': 1920,
        'height': 1080,
        'crop': 'fill',
        'gravity': 'auto',
        'progressive': True,
        'strip': True,
    },
    'video': {
        'quality': 'auto',
        'fetch_format': 'auto',
        'width': 1280,
        'height': 720,
        'bit_rate': '1m',
    }
}

# Cloudinary görsel boyut limitleri
CLOUDINARY_MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB
CLOUDINARY_MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

# Görsel kalite ayarları
CLOUDINARY_IMAGE_QUALITY = 'auto:good'
CLOUDINARY_IMAGE_FORMAT = 'auto'

# File upload optimization
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_PERMISSIONS = 0o644

# GZIP COMPRESSION
USE_GZIP = True
GZIP_CONTENT_TYPES = (
    'text/css',
    'text/javascript',
    'application/javascript',
    'application/x-javascript',
    'text/xml',
    'application/xml',
    'application/xml+rss',
    'text/plain',
    'application/json',
    'application/ld+json',
)

# LOGGING CONFIGURATION
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
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
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# MESSAGE FRAMEWORK
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# PAGINATION SETTINGS
PAGINATE_BY = 12
MAX_PAGE_SIZE = 100

# TRANSLATION SYSTEM
TRANSLATION_SYSTEM_ENABLED = False
AVAILABLE_TRANSLATION_LANGUAGES = ['en', 'de', 'fr', 'es', 'ru', 'ar']

# PERFORMANCE MONITORING
if not DEBUG:
    # Production performance settings
    ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
    
    # Security settings for production
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Debug info
if DEBUG:
    print(f"Cloudinary Storage Package: {CLOUDINARY_STORAGE_LIMIT_GB}GB ({CLOUDINARY_STORAGE_LIMIT_BYTES} bytes)")
    print(f"Cache Backend: {CACHES['default']['BACKEND']}")
    print(f"Compression Enabled: {COMPRESS_ENABLED}")
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(BASE_DIR, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
        


# 2. Çerez ayarları
# Dil çerezi (her zaman aktif - zorunlu)
LANGUAGE_COOKIE_NAME = 'main_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 yıl
LANGUAGE_COOKIE_SECURE = not DEBUG
LANGUAGE_COOKIE_HTTPONLY = False  # JS erişimi için
LANGUAGE_COOKIE_SAMESITE = 'Strict'

# Çerez kategorileri
COOKIE_CATEGORIES = {
    'necessary': {
        'name': 'Zorunlu Çerezler',
        'description': 'Site işlevselliği için gerekli çerezler',
        'always_active': True,
        'cookies': ['sessionid', 'csrftoken', 'main_language', 'dashboard_language']
    },
    'functional': {
        'name': 'Fonksiyonel Çerezler',
        'description': 'Gelişmiş özellikler için çerezler',
        'always_active': False,
        'cookies': ['theme_preference', 'form_data', 'ui_settings']
    },
    'analytics': {
        'name': 'Analitik Çerezler',
        'description': 'Site performansı analizi için çerezler',
        'always_active': False,
        'cookies': ['_ga', '_ga_*', 'page_views', 'session_time']
    },
    'marketing': {
        'name': 'Pazarlama Çerezleri',
        'description': 'Kişiselleştirilmiş reklam için çerezler',
        'always_active': False,
        'cookies': ['marketing_prefs', 'ad_personalization', 'social_tracking']
    }
}