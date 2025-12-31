# PythonAnywhere'e Ücretsiz Deployment Rehberi

Bu rehber, Django projenizi PythonAnywhere'de ücretsiz olarak yayınlamanız için adım adım talimatlar içerir.

## 📋 Gereksinimler

- GitHub hesabı (zaten var ✓)
- PythonAnywhere ücretsiz hesap

---

## 🚀 Adım 1: PythonAnywhere Hesabı Oluşturma

1. **https://www.pythonanywhere.com** adresine gidin
2. **"Start running Python online in less than a minute!"** butonuna tıklayın
3. **Beginner** (ücretsiz) planı seçin
4. Kullanıcı adı ve şifre ile hesap oluşturun

---

## 🔧 Adım 2: Bash Console'u Açma ve Projeyi Klonlama

1. PythonAnywhere dashboard'da **"Consoles"** sekmesine gidin
2. **"Bash"** console'u başlatın
3. Aşağıdaki komutları sırayla çalıştırın:

```bash
# GitHub repo'yu klonlayın
git clone https://github.com/baran725811-art/asdasdasdasdasdqd.git
cd asdasdasdasdasdqd/core

# Repository'yi herkese açık yapmayı unutmayın!
# GitHub → Settings → Change visibility → Make public
```

---

## 🐍 Adım 3: Virtual Environment Kurulumu

```bash
# Python 3.10 ile virtual environment oluşturun
python3.10 -m venv venv

# Virtual environment'ı aktif edin
source venv/bin/activate

# Pip'i güncelleyin
pip install --upgrade pip
```

---

## 📦 Adım 4: Dependencies Yükleme

```bash
# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Eğer hata alırsanız, şu komutla deneyin:
pip install -r requirements.txt --no-cache-dir
```

---

## ⚙️ Adım 5: Environment Variables (.env) Oluşturma

```bash
# .env dosyası oluşturun
nano .env
```

Aşağıdaki içeriği yapıştırın ve **CTRL+X**, **Y**, **ENTER** ile kaydedin:

```env
# Django Core Settings
SECRET_KEY=pythonanywhere-your-username-secret-key-min-50-chars-long-random-string
DEBUG=False
ALLOWED_HOSTS=.pythonanywhere.com

# Database (SQLite - ücretsiz plan için)
# PostgreSQL kullanmıyoruz, SQLite otomatik çalışacak

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com

# Cloudinary Settings (ZORUNLU - resimler için)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_STORAGE_LIMIT=10

# Security Settings (PythonAnywhere için ayarlandı)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
COMPRESS_ENABLED=False

# Email Settings (isteğe bağlı)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
ADMIN_EMAIL=admin@example.com

# Admin URL
ADMIN_URL=admin/
```

**ÖNEMLİ:**
- `yourusername` yazan yerleri kendi PythonAnywhere kullanıcı adınızla değiştirin!
- SECRET_KEY için güçlü rastgele bir string kullanın (en az 50 karakter)
- Cloudinary hesabı için: https://cloudinary.com adresinden ücretsiz hesap açın

---

## 🗄️ Adım 6: Database Migration

```bash
# Veritabanı tablolarını oluşturun
python manage.py migrate

# Superuser (admin) oluşturun
python manage.py createsuperuser
# Kullanıcı adı, email ve şifre girin

# Static dosyaları toplayın
python manage.py collectstatic --noinput
```

---

## 🌐 Adım 7: Web App Oluşturma

1. PythonAnywhere dashboard'da **"Web"** sekmesine gidin
2. **"Add a new web app"** butonuna tıklayın
3. **"Manual configuration"** seçin
4. **Python 3.10** seçin
5. **Next** tıklayın

---

## 📝 Adım 8: Web App Konfigürasyonu

### A) Source code kısmını ayarlayın:

**Source code** bölümünde şu yolu girin:
```
/home/yourusername/asdasdasdasdasdqd/core
```

### B) Virtualenv ayarlayın:

**Virtualenv** bölümünde şu yolu girin:
```
/home/yourusername/asdasdasdasdasdqd/venv
```

### C) WSGI dosyasını düzenleyin:

1. **WSGI configuration file** linkine tıklayın (örn: `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
2. İçeriği tamamen silin
3. Aşağıdaki kodu yapıştırın:

```python
import os
import sys

# Proje yolunu ekle
path = '/home/yourusername/asdasdasdasdasdqd/core'
if path not in sys.path:
    sys.path.insert(0, path)

# Django settings modülünü ayarla
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings.base'

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**ÖNEMLİ:** `yourusername` yazan yerleri kendi kullanıcı adınızla değiştirin!

4. **Save** butonuna tıklayın

---

## 📂 Adım 9: Static Files Ayarları

Web app konfigürasyon sayfasında **"Static files"** bölümüne aşağıdaki yolları ekleyin:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/asdasdasdasdasdqd/core/staticfiles` |
| `/media/` | `/home/yourusername/asdasdasdasdasdqd/core/media` |

---

## 🎉 Adım 10: Siteyi Başlatma

1. Sayfanın en üstündeki yeşil **"Reload yourusername.pythonanywhere.com"** butonuna tıklayın
2. Siteniz şu adreste yayında olacak:
   ```
   https://yourusername.pythonanywhere.com
   ```

---

## 🔐 Admin Paneline Giriş

```
https://yourusername.pythonanywhere.com/admin/
```

Adım 6'da oluşturduğunuz superuser bilgileriyle giriş yapın.

---

## 🎨 Cloudinary Kurulumu (Resim Yüklemeleri için)

1. **https://cloudinary.com** adresine gidin
2. Ücretsiz hesap oluşturun
3. Dashboard'dan şu bilgileri alın:
   - Cloud Name
   - API Key
   - API Secret
4. Bu bilgileri `.env` dosyasındaki ilgili alanlara yazın
5. Web app'i **Reload** edin

---

## 🔄 Kod Güncellemeleri (Push Sonrası)

GitHub'a yeni kod push ettikten sonra PythonAnywhere'de güncellemek için:

```bash
# Bash console'da
cd ~/asdasdasdasdasdqd/core
source ../venv/bin/activate

# Güncellemeleri çek
git pull origin main

# Yeni migrations varsa
python manage.py migrate

# Static dosyaları güncelle
python manage.py collectstatic --noinput
```

Ardından Web sekmesinde **Reload** butonuna basın.

---

## ⚠️ Önemli Notlar

### Ücretsiz Plan Sınırlamaları:
- ✅ 1 web app
- ✅ 512 MB disk alanı
- ✅ SQLite database (PostgreSQL yok)
- ⚠️ Her gün 1 kez "Reload" gerekebilir
- ⚠️ 3 ay hareketsizlik sonrası otomatik durdurulur

### Cloudinary Neden Önemli?
- PythonAnywhere ücretsiz planda disk alanı sınırlı
- Kullanıcıların yüklediği resimler Cloudinary'de saklanır
- Projenizde zaten Cloudinary entegrasyonu var ✓

### SECRET_KEY Oluşturma:
Python console'da çalıştırın:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 🆘 Sorun Giderme

### Hata: "DisallowedHost"
`.env` dosyasındaki `ALLOWED_HOSTS` ve `CSRF_TRUSTED_ORIGINS` ayarlarını kontrol edin.

### Hata: "Static files not loading"
```bash
python manage.py collectstatic --noinput
```
Web app'i Reload edin.

### Hata: "502 Bad Gateway"
- WSGI dosyasındaki yolları kontrol edin
- Error log'ları kontrol edin (Web sekmesinde)

### Database Hatası:
```bash
python manage.py migrate --run-syncdb
```

---

## 📧 Projeyi Paylaşma

Projeniz hazır olduğunda bu linki paylaşın:
```
https://yourusername.pythonanywhere.com
```

**NOT:** Repository'nin public olması gerekir! GitHub → Settings → Change visibility → Make public

---

## 🎯 Sonraki Adımlar

1. Admin panelden içerik ekleyin
2. Cloudinary'e resim yükleyin
3. Site tasarımını kontrol edin
4. Test edin ve paylaşın!

---

## 📞 Yardım Kaynakları

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **PythonAnywhere Forum:** https://www.pythonanywhere.com/forums/
- **Django Docs:** https://docs.djangoproject.com/
- **Cloudinary Docs:** https://cloudinary.com/documentation/django_integration

---

**Başarılar! 🚀**
