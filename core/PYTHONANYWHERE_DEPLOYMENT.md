# PythonAnywhere Deployment Kılavuzu

Bu Django projesini PythonAnywhere'e deploy etmek için adım adım kılavuz.

## 📋 Ön Hazırlık

### 1. PythonAnywhere Hesabı
- [PythonAnywhere](https://www.pythonanywhere.com) hesabı oluşturun
- Başlangıç seviyesi (ücretsiz) veya ücretli plan seçin
- **Önemli**: Ücretsiz planda sadece `username.pythonanywhere.com` kullanılabilir

### 2. Gerekli Bilgiler
Deployment öncesi hazırlayın:
- SECRET_KEY (50+ karakter, güçlü)
- Cloudinary hesap bilgileri (CLOUD_NAME, API_KEY, API_SECRET)
- Email ayarları (Gmail App Password önerilir)
- Domain adı (varsa)

## 🚀 Adım Adım Deployment

### Adım 1: Bash Console Açın
1. PythonAnywhere dashboard'a gidin
2. **Consoles** → **Bash** tıklayın
3. Yeni bir Bash console açılacak

### Adım 2: Projeyi Klonlayın
```bash
# Git yapılandırması (ilk kez kullanıyorsanız)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Projeyi klonlayın
cd ~
git clone https://github.com/baran725811-art/asdasdasdasdasdqd.git
cd asdasdasdasdasdqd/core
```

### Adım 3: Virtual Environment Oluşturun
```bash
# Python 3.10 kullanarak virtual environment oluştur
mkvirtualenv --python=/usr/bin/python3.10 myproject_env

# Virtual environment'ı aktif edin
workon myproject_env

# Gerekli paketleri yükleyin
pip install -r requirements.txt
```

**Önemli**: PythonAnywhere ücretsiz hesaplarda bazı paketler yüklenemeyebilir. Sorun yaşarsanız:
```bash
# Problematik paketleri atlayın
pip install -r requirements.txt --ignore-installed
```

### Adım 4: Environment Variables Ayarlayın
```bash
# .env dosyası oluşturun
nano .env
```

Aşağıdaki içeriği kopyalayın ve **kendi bilgilerinizle** doldurun:

```env
# Django Core Settings
SECRET_KEY=buraya-50-karakterden-uzun-güçlü-bir-key-yazın-random-string
DEBUG=False
DJANGO_ENV=production
ALLOWED_HOSTS=yourusername.pythonanywhere.com

# Database (PythonAnywhere - SQLite kullanacaksanız bu kısmı atlayın)
# PostgreSQL için:
# DB_NAME=your_db_name
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=your-db-host.postgres.pythonanywhere-services.com
# DB_PORT=5432

# HTTPS Settings (PythonAnywhere ücretsiz hesaplarda HTTPS otomatik gelir)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
LANGUAGE_COOKIE_SECURE=True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com

# Email Settings (Gmail App Password kullanın)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-digit-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
ADMIN_EMAIL=admin@yourdomain.com

# Cloudinary Settings
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_STORAGE_LIMIT=10

# Admin Security
ADMIN_URL=gizli-admin-paneli-url/

# Security Monitoring
MAX_LOGIN_ATTEMPTS=3
LOGIN_ATTEMPT_TIMEOUT=600
```

**CTRL+O** ile kaydedin, **CTRL+X** ile çıkın.

### Adım 5: Database Migrations
```bash
# Migrations çalıştır
python manage.py migrate

# Superuser oluştur (admin paneli için)
python manage.py createsuperuser
# Kullanıcı adı, email ve şifre girin

# Static files topla
python manage.py collectstatic --noinput
```

### Adım 6: Web App Oluşturun
1. PythonAnywhere Dashboard → **Web** sekmesi
2. **Add a new web app** tıklayın
3. **Manual configuration** seçin
4. **Python 3.10** seçin
5. **Next** tıklayın

### Adım 7: Web App Ayarları

#### A. Virtualenv Ayarı
Web tab'da **Virtualenv** bölümüne gidin:
```
/home/yourusername/.virtualenvs/myproject_env
```

#### B. WSGI Configuration
1. **Code** bölümünde **WSGI configuration file** linkine tıklayın
2. Açılan dosyadaki **TÜM İÇERİĞİ SİLİN**
3. Aşağıdaki kodu yapıştırın:

```python
# +++++++++++ DJANGO +++++++++++
import os
import sys

# Proje klasörünü path'e ekle
path = '/home/yourusername/asdasdasdasdasdqd/core'
if path not in sys.path:
    sys.path.insert(0, path)

# Django settings modülünü ayarla
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# .env dosyasının yüklenmesini sağla
from pathlib import Path
env_path = Path(path) / '.env'
if env_path.exists():
    from decouple import Config, RepositoryEnv
    config = Config(RepositoryEnv(str(env_path)))

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**DİKKAT**: `yourusername` kısmını kendi PythonAnywhere kullanıcı adınızla değiştirin!

4. **Save** ile kaydedin (CTRL+S)

#### C. Static Files Mapping
Web tab'da **Static files** bölümüne:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/asdasdasdasdasdqd/core/staticfiles/` |
| `/media/` | `/home/yourusername/asdasdasdasdasdqd/core/media/` |

**Add** butonuyla ekleyin.

#### D. Source Code
**Code** bölümünde:
- **Source code**: `/home/yourusername/asdasdasdasdasdqd/core`
- **Working directory**: `/home/yourusername/asdasdasdasdasdqd/core`

### Adım 8: Reload ve Test
1. Web tab'ın en üstünde yeşil **Reload** butonuna tıklayın
2. `https://yourusername.pythonanywhere.com` adresini ziyaret edin
3. Çalışıyorsa ✅, hata varsa logs kontrol edin

## 🐛 Hata Ayıklama

### Error Log Kontrolü
```bash
# Web tab'da "Log files" bölümünden:
# - Error log
# - Server log
# - Access log
```

### Sık Karşılaşılan Hatalar

#### 1. "DisallowedHost" Hatası
```python
# .env dosyasında ALLOWED_HOSTS'u kontrol edin:
ALLOWED_HOSTS=yourusername.pythonanywhere.com
```

#### 2. Static Files Yüklenmiyor
```bash
# Tekrar collectstatic yapın
workon myproject_env
cd ~/asdasdasdasdasdqd/core
python manage.py collectstatic --noinput

# Web tab'da Static files mapping'i kontrol edin
```

#### 3. Database Hatası
```bash
# Migrations tekrar çalıştır
python manage.py migrate --run-syncdb
```

#### 4. "SECRET_KEY" Hatası
```bash
# .env dosyasında SECRET_KEY'in olduğundan emin olun
nano .env
# SECRET_KEY=... satırını kontrol edin
```

## 🔒 Güvenlik Kontrol Listesi

- [ ] SECRET_KEY güçlü ve benzersiz
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS doğru ayarlandı
- [ ] CSRF_TRUSTED_ORIGINS ayarlandı
- [ ] Admin URL değiştirildi (ADMIN_URL)
- [ ] Superuser güçlü şifre
- [ ] .env dosyası git'e eklenmedi (.gitignore'da)
- [ ] Email ayarları test edildi
- [ ] Cloudinary bağlantısı test edildi
- [ ] SSL/HTTPS çalışıyor

## 🔄 Güncelleme (Update)

Kod değişikliklerini deploy etmek için:

```bash
# Bash console'da
cd ~/asdasdasdasdasdqd/core
git pull origin main

# Virtual environment aktif et
workon myproject_env

# Yeni paketler varsa
pip install -r requirements.txt

# Migration varsa
python manage.py migrate

# Static files güncelle
python manage.py collectstatic --noinput

# Web app'i reload et (Web tab'da Reload butonu)
```

## 📊 Database Yönetimi

### SQLite Kullanımı (Ücretsiz Plan)
SQLite production için önerilmez ama başlangıç için yeterli:

```python
# .env dosyasında database ayarları olmadan bırakın
# base.py'deki SQLite ayarı kullanılacak
```

### PostgreSQL Kullanımı (Ücretli Plan)
PythonAnywhere PostgreSQL servisi:

```bash
# Dashboard → Databases → PostgreSQL
# Database oluşturun ve bilgileri .env'e ekleyin
```

## 🎯 Önemli Notlar

1. **Ücretsiz Plan Limitleri**:
   - Sadece HTTPS bağlantıları
   - Sadece whitelisted sitelere API isteği
   - 512MB disk alanı
   - Günlük CPU süresi limiti

2. **Custom Domain** (Ücretli):
   - Web tab → **Add custom domain**
   - DNS ayarlarını yapın
   - ALLOWED_HOSTS ve CSRF_TRUSTED_ORIGINS güncelleyin

3. **Scheduled Tasks**:
   - Dashboard → Tasks
   - Cronjob benzeri görevler ekleyebilirsiniz

4. **Redis/Cache**:
   - Ücretsiz planda Redis yok
   - File-based cache kullanın (base.py'de mevcut)

## 📞 Destek

- PythonAnywhere Forum: https://www.pythonanywhere.com/forums/
- Django Docs: https://docs.djangoproject.com/
- Bu proje için: GitHub Issues

## ✅ Başarılı Deployment Sonrası

1. Admin paneline girin: `https://yourusername.pythonanywhere.com/gizli-admin-paneli-url/`
2. Dashboard'a girin: `https://yourusername.pythonanywhere.com/dashboard/`
3. Site ayarlarını yapılandırın
4. İçerik ekleyin
5. Test edin!

---

**Son Güncelleme**: 2024-12-31
**Django Versiyon**: 5.2.4
**Python Versiyon**: 3.10+
