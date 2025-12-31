"""
WSGI config for PythonAnywhere deployment.

Bu dosyayı PythonAnywhere Web tab'ındaki WSGI configuration file'a kopyalayın.

KULLANIM:
1. PythonAnywhere dashboard -> Web -> WSGI configuration file linkine tıklayın
2. Açılan dosyanın içeriğini tamamen silin
3. Bu dosyanın içeriğini oraya yapıştırın
4. USERNAME kısmını kendi kullanıcı adınızla değiştirin
5. Kaydedin ve Reload butonuna basın
"""

import os
import sys

# ========================
# PYTHONANYWHERE KULLANICI ADI
# ========================
# BURAYA KENDİ PYTHONANYWHERE KULLANICI ADINIZI YAZIN!
USERNAME = 'yourusername'  # <- DEĞİŞTİRİN!

# ========================
# PATH CONFIGURATION
# ========================

# Proje yolu
project_home = f'/home/{USERNAME}/asdasdasdasdasdqd/core'

# Proje yolunu Python path'e ekle
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Virtual environment path (eğer kullanıyorsanız)
virtualenv_path = f'/home/{USERNAME}/.virtualenvs/myenv'  # <- Gerekirse değiştirin

# Virtual environment'ı aktifleştir
if os.path.exists(virtualenv_path):
    activate_this = os.path.join(virtualenv_path, 'bin', 'activate_this.py')
    if os.path.exists(activate_this):
        with open(activate_this) as f:
            exec(f.read(), {'__file__': activate_this})

# ========================
# ENVIRONMENT VARIABLES
# ========================

# Django environment ayarı - PythonAnywhere settings kullan
os.environ['DJANGO_ENV'] = 'pythonanywhere'

# Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# ========================
# DJANGO APPLICATION
# ========================

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

print("🐍 PythonAnywhere WSGI application loaded successfully!")
