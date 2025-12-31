# core/core/settings/development.py
from .base import *
from decouple import config

# Development ayarları
DEBUG = True
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-this-in-production-minimum-50-characters-long!')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# SQLite veritabanı (development için)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend (development için console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'