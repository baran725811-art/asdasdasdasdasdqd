# PythonAnywhere Deployment Rehberi

Bu rehber, Django projenizi PythonAnywhere'de yayına almak için gereken tüm adımları içerir.

## 📋 Ön Hazırlık

### 1. PythonAnywhere Hesabı
- [PythonAnywhere](https://www.pythonanywhere.com) üzerinden hesap oluşturun
- Ücretsiz plan başlangıç için yeterlidir

### 2. Cloudinary Hesabı
- [Cloudinary](https://cloudinary.com) hesabı oluşturun
- Dashboard'dan API bilgilerinizi alın

### 3. Gmail App Password (Email için)
- Gmail hesabınızda 2FA aktif olmalı
- [Google App Passwords](https://myaccount.google.com/apppasswords) sayfasından uygulama şifresi oluşturun

---

## 🚀 Deployment Adımları

### ADIM 1: Kodu PythonAnywhere'e Yükleme

1. PythonAnywhere'de **Bash Console** açın

2. GitHub'dan projeyi klonlayın:
```bash
git clone https://github.com/baran725811-art/asdasdasdasdasdqd.git
cd asdasdasdasdasdqd/core
```

### ADIM 2: Virtual Environment Oluşturma

```bash
# Python 3.10 veya 3.11 virtual environment oluşturun
mkvirtualenv --python=/usr/bin/python3.10 myproject-env

# Virtual environment'i aktif edin (otomatik olur ama emin olmak için)
workon myproject-env

# Paketleri yükleyin
pip install -r requirements.txt
```

### ADIM 3: Environment Variables Ayarlama

1. `.env` dosyası oluşturun:
```bash
cd ~/asdasdasdasdasdqd/core
cp .env.production .env
nano .env
```

2. `.env` dosyasını düzenleyin:

**ÖNEMLİ:** Aşağıdaki değerleri mutlaka değiştirin:

```bash
# SECRET_KEY oluşturun
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Bu komutu çalıştırın ve çıkan SECRET_KEY'i `.env` dosyasına ekleyin.

**Değiştirmeniz gerekenler:**
- `SECRET_KEY` - Yukarıdaki komutla oluşturun
- `ALLOWED_HOSTS` - `KULLANICI_ADI.pythonanywhere.com` şeklinde düzenleyin
- `CSRF_TRUSTED_ORIGINS` - `https://KULLANICI_ADI.pythonanywhere.com`
- Email ayarları (Gmail ve App Password)
- Cloudinary bilgileri

### ADIM 4: Veritabanı ve Statik Dosyalar

```bash
# Veritabanı migrasyonları
python manage.py migrate

# Statik dosyaları toplama
python manage.py collectstatic --noinput

# Superuser oluşturma (admin paneli için)
python manage.py createsuperuser

# Cache klasörü oluşturma
mkdir -p ~/asdasdasdasdasdqd/core/cache
chmod 755 ~/asdasdasdasdasdqd/core/cache

# Logs klasörü oluşturma
mkdir -p ~/asdasdasdasdasdqd/core/logs
chmod 755 ~/asdasdasdasdasdqd/core/logs
```

### ADIM 5: Web App Oluşturma

1. PythonAnywhere Dashboard'da **Web** sekmesine gidin
2. **Add a new web app** tıklayın
3. **Manual configuration** seçin
4. **Python 3.10** seçin

### ADIM 6: WSGI Dosyasını Yapılandırma

Web sekmesinde **WSGI configuration file** linkine tıklayın ve dosyayı şöyle düzenleyin:

```python
import os
import sys

# Proje yolunu ekle
path = '/home/KULLANICI_ADI/asdasdasdasdasdqd/core'
if path not in sys.path:
    sys.path.append(path)

# Django environment ayarı
os.environ['DJANGO_ENV'] = 'production'
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# Virtual environment'i aktif et
# PythonAnywhere otomatik yapar, bu satır opsiyonel

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**ÖNEMLİ:** `KULLANICI_ADI` yerine kendi kullanıcı adınızı yazın!

### ADIM 7: Virtual Environment Ayarlama

Web sekmesinde **Virtualenv** bölümüne:
```
/home/KULLANICI_ADI/.virtualenvs/myproject-env
```

### ADIM 8: Static Files Mapping

Web sekmesinde **Static files** bölümüne ekleyin:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/KULLANICI_ADI/asdasdasdasdasdqd/core/staticfiles` |
| `/media/` | `/home/KULLANICI_ADI/asdasdasdasdasdqd/core/media` |

### ADIM 9: Reload & Test

1. Web sekmesinde yeşil **Reload** butonuna tıklayın
2. Sitenizi ziyaret edin: `https://KULLANICI_ADI.pythonanywhere.com`

---

## ⚙️ Önemli Konfigürasyonlar

### Admin Panel Erişimi

Admin panel URL'ini güvenlik için değiştirdik. `.env` dosyasında:
```
ADMIN_URL=gizli-admin-paneli-xyz123/
```

Admin panele erişmek için:
```
https://KULLANICI_ADI.pythonanywhere.com/gizli-admin-paneli-xyz123/
```

### SSL/HTTPS

PythonAnywhere ücretsiz SSL sertifikası sunar. Web sekmesinde **HTTPS** bölümünden:
- **Force HTTPS** seçeneğini aktif edin

### Güncellemeler

Kodu güncelledikten sonra:
```bash
cd ~/asdasdasdasdasdqd/core
git pull
workon myproject-env
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Sonra Web sekmesinde **Reload** butonuna tıklayın.

---

## 🔧 Sorun Giderme

### Error Log'larını İnceleme

PythonAnywhere'de:
1. Web sekmesinde **Error log** ve **Server log** linklerine tıklayın
2. Veya projedeki log dosyalarını kontrol edin:
```bash
cat ~/asdasdasdasdasdqd/core/logs/django.log
cat ~/asdasdasdasdasdqd/core/logs/security.log
```

### Yaygın Sorunlar

**1. Import Hataları**
- Virtual environment'in doğru aktif olduğundan emin olun
- `pip list` ile paketlerin yüklü olduğunu kontrol edin

**2. Static Files Yüklenmiyor**
- `collectstatic` komutunu çalıştırdınız mı?
- Static files mapping'i doğru mu?

**3. Database Hataları**
- Migration'ları çalıştırdınız mı: `python manage.py migrate`

**4. 500 Internal Server Error**
- Error log'ları kontrol edin
- `.env` dosyasının doğru olduğundan emin olun
- `DEBUG=True` yapıp hatayı görebilirsiniz (sonra tekrar False yapın!)

### Debug Modu Açma (Geçici)

**SADECE** hata tespiti için `.env` dosyasında:
```
DEBUG=True
```

Hatayı bulduktan sonra **MUTLAKA** tekrar:
```
DEBUG=False
```

---

## 📊 Performans Optimizasyonu

### 1. Cache Temizleme

Periyodik olarak cache'i temizleyin:
```bash
rm -rf ~/asdasdasdasdasdqd/core/cache/*
```

### 2. Log Dosyaları

Log dosyaları büyüdükçe:
```bash
# Log dosyalarını temizle
> ~/asdasdasdasdasdqd/core/logs/django.log
> ~/asdasdasdasdasdqd/core/logs/security.log
```

### 3. Scheduled Tasks (Ücretli Plan)

Ücretli planda scheduled tasks ile otomatik bakım:
- Log temizleme
- Cache temizleme
- Veritabanı optimizasyonu

---

## 🔒 Güvenlik Checklist

- [ ] `SECRET_KEY` güçlü ve unique
- [ ] `DEBUG=False` production'da
- [ ] `ALLOWED_HOSTS` sadece domain'inizi içeriyor
- [ ] Admin URL değiştirildi
- [ ] HTTPS Force aktif
- [ ] Email App Password kullanılıyor (gerçek şifre değil)
- [ ] Cloudinary API secrets güvenli
- [ ] `.env` dosyası git'e eklenmedi (.gitignore'da)

---

## 📞 Destek

**PythonAnywhere Dokümantasyonu:**
- https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/

**Django Dokümantasyonu:**
- https://docs.djangoproject.com/en/stable/howto/deployment/

**Proje GitHub:**
- https://github.com/baran725811-art/asdasdasdasdasdqd

---

## 🎉 Başarılı Deployment!

Tebrikler! Projeniz artık yayında. Başarılı deployment için:

1. ✅ Siteyi test edin: `https://KULLANICI_ADI.pythonanywhere.com`
2. ✅ Admin panele giriş yapın
3. ✅ Tüm sayfaların çalıştığını kontrol edin
4. ✅ Form gönderimlerini test edin
5. ✅ Email gönderimini test edin

**İyi çalışmalar! 🚀**
