# core/settings/__init__.py
"""
Settings modülü - Otomatik environment seçimi
Development veya Production ayarlarını otomatik import eder
"""

import os

# DJANGO_SETTINGS_MODULE environment variable'ından ayarları al
# Eğer set edilmemişse, DEBUG değişkenine göre karar ver
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *
