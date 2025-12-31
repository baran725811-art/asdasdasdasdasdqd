# PythonAnywhere Ücretsiz Deployment Rehberi

Bu rehber, Django projenizi PythonAnywhere ücretsiz hesabında yayınlamanız için adım adım talimatlar içerir.

## 📋 Ön Hazırlık

### 1. PythonAnywhere Hesabı Oluşturun
- [PythonAnywhere](https://www.pythonanywhere.com) adresine gidin
- Ücretsiz hesap oluşturun (Beginner Account)
- Kullanıcı adınızı not edin (örn: `kullaniciadi`)

### 2. Gerekli Bilgileri Hazırlayın
Aşağıdaki bilgilere ihtiyacınız olacak:
- GitHub repository URL'niz
- Django SECRET_KEY (50+ karakter)
- Email ayarları (SMTP)
- Cloudinary API bilgileri (opsiyonel)
- DeepL API key (opsiyonel)

---

## 🚀 Adım Adım Deployment

### ADIM 1: Bash Console Açın
1. PythonAnywhere dashboard'da **"Consoles"** sekmesine gidin
2. **"Bash"** console başlatın

### ADIM 2: Projeyi Klonlayın
```bash
# GitHub'dan projeyi klonlayın
git clone https://github.com/kullaniciadi/proje-adi.git
cd proje-adi/core
```

### ADIM 3: Virtual Environment Oluşturun
```bash
# Virtual environment oluştur
mkvirtualenv --python=/usr/bin/python3.10 myenv

# Aktif olduğunu kontrol edin (başında (myenv) olmalı)
# Paketleri yükleyin
pip install -r requirements.txt
```

### ADIM 4: MySQL Veritabanı Oluşturun
1. PythonAnywhere dashboard'da **"Databases"** sekmesine gidin
2. MySQL şifrenizi ayarlayın
3. Yeni veritabanı oluşturun:
   - Database name: `kullaniciadi$proje` (örn: `johndoe$myproject`)
4. Veritabanı bilgilerini not edin:
   - Host: `kullaniciadi.mysql.pythonanywhere-services.com`
   - Username: `kullaniciadi`
   - Password: [sizin şifreniz]
   - Database: `kullaniciadi$proje`

### ADIM 5: Environment Variables (.env) Oluşturun
```bash
cd ~/proje-adi/core
nano .env
```

Aşağıdaki içeriği yapıştırın ve **kendi bilgilerinizle** doldurun:

```bash
# Django Core Settings
DJANGO_SETTINGS_MODULE=core.settings.pythonanywhere
SECRET_KEY=buraya-50-karakterden-uzun-rastgele-bir-key-yazin-123456789
DEBUG=False
ALLOWED_HOSTS=kullaniciadi.pythonanywhere.com

# Database Settings - MySQL
DB_NAME=kullaniciadi$proje
DB_USER=kullaniciadi
DB_PASSWORD=mysql-sifreniz
DB_HOST=kullaniciadi.mysql.pythonanywhere-services.com
DB_PORT=3306

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://kullaniciadi.pythonanywhere.com

# Email Settings (Gmail örneği)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sizin-email@gmail.com
EMAIL_HOST_PASSWORD=gmail-app-password
DEFAULT_FROM_EMAIL=sizin-email@gmail.com
ADMIN_EMAIL=admin@gmail.com

# Cloudinary (opsiyonel - medya dosyaları için)
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Admin Security
ADMIN_URL=guvenli-admin-paneli-xyz123/

# PythonAnywhere Domain
PYTHONANYWHERE_DOMAIN=kullaniciadi.pythonanywhere.com
```

**Önemli Notlar:**
- `SECRET_KEY`: [Bu linke tıklayın](https://djecrety.ir/) ve rastgele key oluşturun
- Gmail kullanıyorsanız: [2-Factor App Password](https://myaccount.google.com/apppasswords) oluşturun
- Cloudinary kullanmak istemiyorsanız: `USE_CLOUDINARY=False` yapın

CTRL+X → Y → ENTER ile kaydedin.

### ADIM 6: Veritabanı Migrasyonları
```bash
# Virtual environment'ı aktif edin (gerekirse)
workon myenv

cd ~/proje-adi/core

# Migrasyonları çalıştırın
python manage.py migrate --settings=core.settings.pythonanywhere

# Static dosyaları toplayın
python manage.py collectstatic --noinput --settings=core.settings.pythonanywhere

# Superuser oluşturun
python manage.py createsuperuser --settings=core.settings.pythonanywhere
```

### ADIM 7: Web App Oluşturun
1. PythonAnywhere dashboard'da **"Web"** sekmesine gidin
2. **"Add a new web app"** tıklayın
3. Domain: `kullaniciadi.pythonanywhere.com` (otomatik gelir)
4. **"Manual configuration"** seçin
5. Python version: **Python 3.10** seçin

### ADIM 8: WSGI Dosyasını Yapılandırın
1. Web tab'da **"WSGI configuration file"** linkine tıklayın
2. Tüm içeriği silin ve aşağıdakini yapıştırın:

```python
import os
import sys

# Proje yolunu ekle
path = '/home/kullaniciadi/proje-adi/core'
if path not in sys.path:
    sys.path.insert(0, path)

# Virtual environment
virtualenv_path = '/home/kullaniciadi/.virtualenvs/myenv'
activate_this = os.path.join(virtualenv_path, 'bin', 'activate_this.py')

# Python 3.10+ için exec kullanımı
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# .env dosyasını yükle
from pathlib import Path
env_path = Path('/home/kullaniciadi/proje-adi/core/.env')
if env_path.exists():
    from decouple import Config, RepositoryEnv
    config = Config(RepositoryEnv(str(env_path)))

# Django ayarları
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.pythonanywhere')

# Django uygulamasını yükle
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Önemli:** `kullaniciadi` ve `proje-adi` yazan yerleri değiştirin!

### ADIM 9: Virtual Environment Ayarlayın
Web tab'da:
1. **"Virtualenv"** bölümünü bulun
2. Path: `/home/kullaniciadi/.virtualenvs/myenv`

### ADIM 10: Static Files Yapılandırması
Web tab'da **"Static files"** bölümüne:

| URL           | Directory                                    |
|---------------|----------------------------------------------|
| `/static/`    | `/home/kullaniciadi/proje-adi/core/staticfiles` |
| `/media/`     | `/home/kullaniciadi/proje-adi/core/media`       |

### ADIM 11: Reload ve Test
1. Web tab'da yeşil **"Reload"** butonuna tıklayın
2. Sitenize gidin: `https://kullaniciadi.pythonanywhere.com`
3. Admin paneline erişin: `https://kullaniciadi.pythonanywhere.com/guvenli-admin-paneli-xyz123/`

---

## ✅ Deployment Checklist

- [ ] PythonAnywhere hesabı oluşturuldu
- [ ] Proje GitHub'dan klonlandı
- [ ] Virtual environment kuruldu
- [ ] `requirements.txt` paketleri yüklendi
- [ ] MySQL veritabanı oluşturuldu
- [ ] `.env` dosyası yapılandırıldı
- [ ] Migrasyonlar çalıştırıldı
- [ ] Static dosyalar toplandı (`collectstatic`)
- [ ] Superuser oluşturuldu
- [ ] Web app oluşturuldu
- [ ] WSGI dosyası yapılandırıldı
- [ ] Virtual environment path ayarlandı
- [ ] Static files mapping yapıldı
- [ ] Site reload edildi
- [ ] Site erişilebilir durumda

---

## 🔧 Güncelleme ve Yeniden Deployment

Kod değişiklikleri yaptığınızda:

```bash
# Bash console'da
cd ~/proje-adi/core
git pull origin main

# Virtual environment aktif
workon myenv

# Gerekirse yeni paketleri yükle
pip install -r requirements.txt

# Yeni migrasyonlar varsa
python manage.py migrate --settings=core.settings.pythonanywhere

# Static dosyaları güncelle
python manage.py collectstatic --noinput --settings=core.settings.pythonanywhere
```

Sonra Web tab'dan **Reload** edin.

---

## 🐛 Hata Giderme

### 1. "ImportError" veya "Module not found"
**Çözüm:**
```bash
workon myenv
pip install -r requirements.txt
```

### 2. "OperationalError: no such table"
**Çözüm:**
```bash
python manage.py migrate --settings=core.settings.pythonanywhere
```

### 3. Static dosyalar yüklenmiyor
**Çözüm:**
```bash
python manage.py collectstatic --noinput --settings=core.settings.pythonanywhere
```
Web tab'da static files mapping'i kontrol edin.

### 4. "500 Internal Server Error"
**Çözüm:**
- Web tab'da **"Error log"** linkine tıklayın
- Son satırlara bakın
- Hatayı okuyun ve düzeltin

### 5. Admin paneline erişemiyorum
**Kontrol:**
- `.env` dosyasında `ADMIN_URL` değerini kontrol edin
- URL: `https://kullaniciadi.pythonanywhere.com/{ADMIN_URL}/`

### 6. CSRF verification failed
**Çözüm:** `.env` dosyasında:
```
CSRF_TRUSTED_ORIGINS=https://kullaniciadi.pythonanywhere.com
```

---

## 📝 Önemli Notlar

### PythonAnywhere Ücretsiz Hesap Kısıtlamaları:
- ✅ 512MB disk alanı
- ✅ 1 web app
- ✅ MySQL veritabanı (512MB)
- ❌ Redis cache yok (file-based cache kullanılıyor)
- ❌ SSH erişimi yok
- ❌ Scheduled tasks (3 aylık hesaplar için)
- ⚠️ 3 ay boyunca giriş yapmazsanız hesap suspend olur

### Güvenlik Önerileri:
1. **SECRET_KEY**: Asla paylaşmayın, GitHub'a push etmeyin
2. **Admin URL**: Default `admin/` yerine özel URL kullanın
3. **Cloudinary**: Medya dosyaları için kullanın (ücretsiz tier)
4. **HTTPS**: PythonAnywhere otomatik sağlar
5. **Backup**: Düzenli olarak veritabanı yedeği alın

### Performans İpuçları:
1. `COMPRESS_ENABLED=True` ile CSS/JS sıkıştırması aktif
2. Template caching aktif
3. File-based cache kullanılıyor
4. Static files için Cloudflare CDN kullanabilirsiniz (opsiyonel)

---

## 🆘 Yardım ve Destek

- **PythonAnywhere Forum**: https://www.pythonanywhere.com/forums/
- **Django Docs**: https://docs.djangoproject.com/
- **PythonAnywhere Help**: https://help.pythonanywhere.com/

---

## 📌 Son Kontroller

Deployment başarılı mı?

1. Ana sayfa açılıyor mu? → `https://kullaniciadi.pythonanywhere.com`
2. Admin paneline giriş yapabiliyorsunuz mu?
3. Dil değiştirme çalışıyor mu?
4. İletişim formu çalışıyor mu?
5. Resimler yükleniyor mu?
6. Ürünler sayfası açılıyor mu?

✅ Hepsi tamam mı? Tebrikler, deployment başarılı! 🎉

---

**Son Güncelleme:** 2025-12-31
**Django Versiyon:** 5.2.4
**Python Versiyon:** 3.10
