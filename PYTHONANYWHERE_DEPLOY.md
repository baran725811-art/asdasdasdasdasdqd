# PythonAnywhere Deploy Talimatları

Bu belge, Django projenizi PythonAnywhere'e nasıl deploy edeceğinizi adım adım anlatmaktadır.

## Ön Hazırlık

### 1. PythonAnywhere Hesabı Oluşturun
- [PythonAnywhere](https://www.pythonanywhere.com) adresinden ücretsiz hesap oluşturun
- Ücretsiz hesap özellikleri:
  - 1 web app
  - kullaniciadi.pythonanywhere.com domain
  - 512MB disk alanı
  - MySQL veritabanı (1 adet)
  - SQLite kullanabilirsiniz

### 2. Gerekli Bilgileri Hazırlayın
Aşağıdaki bilgilere ihtiyacınız olacak:
- Gmail hesabı ve App Password (email gönderimi için)
- Cloudinary hesabı (medya dosyaları için)
- SECRET_KEY (güvenlik anahtarı)

---

## Adım 1: PythonAnywhere'de Proje Dosyalarını Hazırlama

### 1.1. Bash Console Açın
- PythonAnywhere Dashboard > Consoles > Bash
- Yeni bir Bash console açın

### 1.2. Projeyi GitHub'dan Klonlayın
```bash
# Ana dizinde olduğunuzdan emin olun
cd ~

# Projeyi klonlayın
git clone https://github.com/baran725811-art/asdasdasdasdasdqd.git

# Proje dizinine girin
cd asdasdasdasdasdqd
```

---

## Adım 2: Virtual Environment Oluşturma

### 2.1. Virtual Environment Oluşturun
```bash
# .virtualenvs klasörü oluşturun (yoksa)
mkdir -p ~/.virtualenvs

# Python 3.10 ile virtual environment oluşturun
python3.10 -m venv ~/.virtualenvs/django_env

# Virtual environment'ı aktifleştirin
source ~/.virtualenvs/django_env/bin/activate
```

### 2.2. Pip'i Güncelleyin
```bash
pip install --upgrade pip
```

### 2.3. Proje Bağımlılıklarını Yükleyin
```bash
# Proje core dizinine gidin
cd ~/asdasdasdasdasdqd/core

# Requirements'ları yükleyin
pip install -r requirements.txt
```

**ÖNEMLİ:** Eğer `psycopg2-binary` hatası alırsanız (ücretsiz hesaplarda PostgreSQL yok):
```bash
# requirements.txt'den psycopg2-binary satırını kaldırın veya
pip install -r requirements.txt --ignore-installed psycopg2-binary
```

**MySQL kullanacaksanız:**
```bash
pip install mysqlclient
```

---

## Adım 3: Environment Variables (.env) Ayarlama

### 3.1. .env Dosyası Oluşturun
```bash
cd ~/asdasdasdasdasdqd/core
cp .env.pythonanywhere .env
```

### 3.2. .env Dosyasını Düzenleyin
```bash
nano .env
```

### 3.3. SECRET_KEY Oluşturun
Python shell'de şu komutu çalıştırın:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Çıktıyı kopyalayın ve .env dosyasındaki SECRET_KEY'e yapıştırın.

### 3.4. .env Dosyasında Değiştirmeniz Gerekenler
```bash
# KULLANICI ADI
# Tüm 'kullaniciadi' yazan yerleri kendi PythonAnywhere kullanıcı adınızla değiştirin

ALLOWED_HOSTS=kullaniciadi.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://kullaniciadi.pythonanywhere.com

# MySQL ayarları (eğer MySQL kullanıyorsanız)
DB_NAME=kullaniciadi$veritabani_adi
DB_USER=kullaniciadi
DB_PASSWORD=mysql_sifreniz
DB_HOST=kullaniciadi.mysql.pythonanywhere-services.com

# Email ayarları
EMAIL_HOST_USER=sizin-email@gmail.com
EMAIL_HOST_PASSWORD=gmail-app-password
DEFAULT_FROM_EMAIL=sizin-email@gmail.com
ADMIN_EMAIL=sizin-email@gmail.com

# Cloudinary (https://cloudinary.com/console)
CLOUDINARY_CLOUD_NAME=cloud-adi
CLOUDINARY_API_KEY=api-key
CLOUDINARY_API_SECRET=api-secret
```

Ctrl+X > Y > Enter ile kaydedin.

---

## Adım 4: Veritabanı Kurulumu

### Seçenek A: SQLite Kullanımı (Kolay, küçük projeler için)

#### 4.1. Settings Dosyasını SQLite için Düzenleyin
```bash
nano ~/asdasdasdasdasdqd/core/core/settings/production.py
```

DATABASES bölümünü şu şekilde değiştirin:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### 4.2. Cache Ayarlarını Düzenleyin
Redis yerine file-based cache kullanın:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 3600,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
        },
    }
}
```

### Seçenek B: MySQL Kullanımı (Önerilir)

#### 4.1. MySQL Veritabanı Oluşturun
- PythonAnywhere Dashboard > Databases
- MySQL password ayarlayın
- "Create database" butonuna tıklayın (örn: kullaniciadi$django_db)

#### 4.2. .env Dosyasında MySQL Ayarlarını Yapın
Yukarıdaki Adım 3.4'teki MySQL ayarlarını doldurun.

#### 4.3. mysqlclient Yükleyin
```bash
source ~/.virtualenvs/django_env/bin/activate
pip install mysqlclient
```

---

## Adım 5: Django Migrasyonları ve Static Files

### 5.1. Migrasyonları Çalıştırın
```bash
cd ~/asdasdasdasdasdqd/core
source ~/.virtualenvs/django_env/bin/activate

# Production settings ile migrate
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py migrate
```

### 5.2. Superuser Oluşturun
```bash
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py createsuperuser
```

### 5.3. Static Dosyaları Toplayın
```bash
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py collectstatic --noinput
```

### 5.4. Çeviri Dosyalarını Derleyin
```bash
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py compilemessages
```

---

## Adım 6: Web App Yapılandırması

### 6.1. Web App Oluşturun
- PythonAnywhere Dashboard > Web
- "Add a new web app" butonuna tıklayın
- Domain: kullaniciadi.pythonanywhere.com (otomatik gelir)
- **"Manual configuration"** seçin (Django seçmeyin!)
- Python version: 3.10 seçin

### 6.2. Virtualenv Ayarlayın
- Web tab'da "Virtualenv" bölümünü bulun
- Virtualenv path: `/home/kullaniciadi/.virtualenvs/django_env`
- Enter'a basın

### 6.3. WSGI Configuration File'ı Düzenleyin
- Web tab'da "Code" bölümünde "WSGI configuration file" linkine tıklayın
- Dosyanın içeriğini **tamamen silin**
- `~/asdasdasdasdasdqd/core/pythonanywhere_wsgi.py` dosyasının içeriğini kopyalayıp yapıştırın

**ÖNEMLİ:** Dosyada şu değişikliği yapın:
```python
USERNAME = 'kullaniciadi'  # Kendi kullanıcı adınızı yazın
```

Kaydet (Save) butonuna basın.

### 6.4. Static Files Ayarları
Web tab'da "Static files" bölümüne gidin:

| URL | Directory |
|-----|-----------|
| /static/ | /home/kullaniciadi/asdasdasdasdasdqd/core/staticfiles/ |
| /media/ | /home/kullaniciadi/asdasdasdasdasdqd/core/media/ |

**Not:** Cloudinary kullanıyorsanız /media/ gerekmez.

### 6.5. Reload Web App
- Web tab'ın en üstünde yeşil "Reload kullaniciadi.pythonanywhere.com" butonuna basın

---

## Adım 7: Test ve Kontrol

### 7.1. Siteyi Ziyaret Edin
- https://kullaniciadi.pythonanywhere.com adresine gidin
- Siteniz çalışıyor olmalı!

### 7.2. Admin Paneline Giriş Yapın
- https://kullaniciadi.pythonanywhere.com/admin/ (veya .env'de ayarladığınız ADMIN_URL)
- Oluşturduğunuz superuser ile giriş yapın

### 7.3. Hata Kontrolü
Eğer hata alırsanız:
- Web tab'da "Log files" bölümündeki error log'u kontrol edin
- Bash console'da şunu çalıştırın:
```bash
tail -50 /var/log/kullaniciadi.pythonanywhere.com.error.log
```

---

## Adım 8: Güvenlik Ayarları

### 8.1. Admin URL'i Değiştirin
.env dosyasında:
```bash
ADMIN_URL=super-gizli-admin-xyz123/
```

### 8.2. Debug Modunu Kapatın
.env dosyasında mutlaka:
```bash
DEBUG=False
```

### 8.3. HTTPS Ayarları
PythonAnywhere otomatik HTTPS sağlar, .env'de:
```bash
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## Güncellemeler ve Bakım

### Kod Güncellemesi
```bash
cd ~/asdasdasdasdasdqd
git pull origin main

cd core
source ~/.virtualenvs/django_env/bin/activate

# Yeni bağımlılıklar varsa
pip install -r requirements.txt

# Migrations varsa
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py migrate

# Static files güncellemesi
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py collectstatic --noinput

# Web app'i reload et (Web tab'dan)
```

### Veritabanı Backup
```bash
# SQLite
cp ~/asdasdasdasdasdqd/core/db.sqlite3 ~/backups/db_$(date +%Y%m%d).sqlite3

# MySQL
mysqldump -u kullaniciadi -h kullaniciadi.mysql.pythonanywhere-services.com \
  -p kullaniciadi\$veritabani_adi > ~/backups/db_$(date +%Y%m%d).sql
```

---

## Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. ImportError: No module named 'django'
**Çözüm:** Virtual environment doğru ayarlanmamış
- WSGI dosyasında virtualenv yolunu kontrol edin
- Web tab'da Virtualenv ayarını kontrol edin

### 2. DisallowedHost at /
**Çözüm:** .env dosyasında ALLOWED_HOSTS yanlış
```bash
ALLOWED_HOSTS=kullaniciadi.pythonanywhere.com
```

### 3. Static files yüklenmiyor
**Çözüm:**
- collectstatic çalıştırın
- Web tab'da Static files yollarını kontrol edin
- STATIC_ROOT doğru ayarlanmış mı kontrol edin

### 4. Database connection error
**Çözüm:**
- MySQL şifresini doğru mu girdiniz?
- Database adı doğru mu? (kullaniciadi$db_adi formatında olmalı)
- .env dosyasında DB_HOST doğru mu?

### 5. 500 Internal Server Error
**Çözüm:**
- Error log'u kontrol edin
- DEBUG=True yapıp hatayı görün (sonra False'a çevirmeyi unutmayın)
- WSGI dosyasında USERNAME doğru mu?

---

## Gmail App Password Alma

1. Google hesabınıza gidin: https://myaccount.google.com/
2. Security > 2-Step Verification (2 adımlı doğrulamayı aktif edin)
3. Security > App passwords
4. "Select app" > Mail
5. "Select device" > Other (Custom name) > "Django App"
6. Generate
7. Çıkan 16 karakterlik şifreyi .env'deki EMAIL_HOST_PASSWORD'e yazın

---

## Cloudinary Kurulumu

1. https://cloudinary.com/ adresine gidin
2. Ücretsiz hesap oluşturun
3. Dashboard'a gidin
4. "Product Environment Credentials" bölümünden:
   - Cloud name
   - API Key
   - API Secret

   bilgilerini alın ve .env dosyasına yazın

---

## Destek ve Kaynaklar

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/

---

## Lisans ve İletişim

Herhangi bir sorun için GitHub repository'nizde issue açabilirsiniz.

**Başarılar! 🚀**
