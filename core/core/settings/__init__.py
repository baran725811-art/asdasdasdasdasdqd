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
    print(f"🚀 Production settings loaded")
elif DJANGO_ENV == 'pythonanywhere':
    from .pythonanywhere import *
    print(f"🐍 PythonAnywhere settings loaded")
elif DJANGO_ENV == 'test':
    from .development import *
    print(f"🧪 Test settings loaded")
else:
    from .development import *
    print(f"🔧 Development settings loaded")
