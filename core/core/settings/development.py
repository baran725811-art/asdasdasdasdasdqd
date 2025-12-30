#core\core\settings\development.py
from .base import *
from decouple import config

DEBUG = True
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-this-in-production-minimum-50-characters-long!')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Development - SSL/HTTPS ayarları kapalı
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}