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