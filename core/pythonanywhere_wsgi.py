# ===================================================================
# PYTHONANYWHERE WSGI YAPıLANDıRMA DOSYASI
# ===================================================================
# Bu dosya PythonAnywhere'de Web App oluştururken kullanılacak WSGI dosyasıdır.
#
# PythonAnywhere Web tab'inde:
# 1. "Add a new web app" butonuna tıklayın
# 2. Domain adınızı seçin (örn: kullaniciadi.pythonanywhere.com)
# 3. "Manual configuration" seçin (Django seçmeyin!)
# 4. Python versiyonunuzu seçin (3.10 veya üstü önerilir)
# 5. WSGI configuration file'ı açın ve bu dosyanın içeriğini oraya yapıştırın
# ===================================================================

import os
import sys

# ===================================================================
# 1. PROJE YOLLARı AYARLARI
# ===================================================================
# PythonAnywhere'deki kullanıcı adınızı buraya yazın
# Örnek: '/home/kullaniciadi/...'
USERNAME = 'kullaniciadi'  # *** BU SATIRI DEĞİŞTİRİN ***

# Proje dizin yolu
project_home = f'/home/{USERNAME}/asdasdasdasdasdqd'

# Core klasörü (manage.py'nin bulunduğu yer)
project_core = os.path.join(project_home, 'core')

# Projeyi Python path'e ekle
if project_home not in sys.path:
    sys.path.insert(0, project_home)

if project_core not in sys.path:
    sys.path.insert(0, project_core)

# ===================================================================
# 2. VIRTUAL ENVIRONMENT AKTİFLEŞTİRME
# ===================================================================
# Virtual environment'ınızın yolu
# PythonAnywhere'de genellikle: /home/kullaniciadi/.virtualenvs/venv_adi/
venv_path = f'/home/{USERNAME}/.virtualenvs/django_env'  # *** GEREKIRSE DEĞİŞTİRİN ***

# Virtual environment'ı aktifleştir
activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# ===================================================================
# 3. ENVIRONMENT VARIABLES (.env dosyası)
# ===================================================================
# .env dosyasını yükle
env_path = os.path.join(project_core, '.env')

# .env dosyasını manuel olarak yükle (python-decouple kullanıyoruz)
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# ===================================================================
# 4. DJANGO SETTINGS MODULE
# ===================================================================
# Production ayarlarını kullan
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')

# ===================================================================
# 5. DJANGO APPLICATION
# ===================================================================
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# ===================================================================
# NOTLAR:
# ===================================================================
# 1. Bu dosyayı PythonAnywhere Web tab'ındaki WSGI configuration file'a kopyalayın
# 2. USERNAME değişkenini kendi kullanıcı adınızla değiştirin
# 3. Virtual environment yolunu kontrol edin
# 4. .env dosyasını core/ klasörüne yükleyin
# 5. Static files: Web tab'da "Static files" bölümünde şunları ayarlayın:
#    URL: /static/
#    Directory: /home/USERNAME/asdasdasdasdasdqd/core/staticfiles/
# 6. Media files: (Cloudinary kullanıyorsanız gerekli değil)
#    URL: /media/
#    Directory: /home/USERNAME/asdasdasdasdasdqd/core/media/
# ===================================================================
