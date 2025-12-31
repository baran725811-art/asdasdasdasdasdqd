"""
Django Settings Package
Environment-based settings loader.
"""
import os
from decouple import config

# Environment detection (default: development)
DJANGO_ENV = config('DJANGO_ENV', default='development')

# Import settings based on environment
if DJANGO_ENV == 'production':
    from .production import *
elif DJANGO_ENV == 'test':
    from .development import *
else:
    from .development import *
