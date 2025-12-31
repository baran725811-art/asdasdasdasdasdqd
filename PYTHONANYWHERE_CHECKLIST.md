# PythonAnywhere Deploy Kontrol Listesi

Bu belge, PythonAnywhere'e deploy yapmadan önce kontrol etmeniz gereken adımları içerir.

## ✅ Deployment Öncesi Kontrol Listesi

### 1. Dosya Kontrolü
- [ ] `core/.env.pythonanywhere` dosyasını `.env` olarak kopyaladınız mı?
- [ ] `.env` dosyasındaki tüm değerleri doldurdunuz mu?
- [ ] `SECRET_KEY` oluşturdunuz mu?
- [ ] `pythonanywhere_wsgi.py` dosyasını kontrol ettiniz mi?

### 2. Environment Variables (.env)
- [ ] `SECRET_KEY` - Güçlü bir anahtar oluşturdunuz mu?
- [ ] `DEBUG=False` - Debug modunu kapattınız mı?
- [ ] `ALLOWED_HOSTS` - PythonAnywhere domain'inizi eklediniz mi?
- [ ] `CSRF_TRUSTED_ORIGINS` - HTTPS domain'inizi eklediniz mi?
- [ ] `ADMIN_URL` - Admin URL'ini değiştirdiniz mi?

### 3. Veritabanı Ayarları
#### SQLite Kullanıyorsanız:
- [ ] `.env` dosyasında `DB_ENGINE=django.db.backends.sqlite3`

#### MySQL Kullanıyorsanız:
- [ ] PythonAnywhere'de MySQL password ayarladınız mı?
- [ ] MySQL veritabanı oluşturdunuz mu?
- [ ] `.env` dosyasında MySQL ayarlarını yaptınız mı?
- [ ] `DB_ENGINE=django.db.backends.mysql` ayarladınız mı?
- [ ] `DB_NAME=kullaniciadi$veritabani_adi` formatında mı?
- [ ] `mysqlclient` paketini yüklediniz mi?

### 4. Email Ayarları
- [ ] Gmail hesabınız var mı?
- [ ] 2-Factor Authentication aktif mi?
- [ ] App Password oluşturdunuz mu?
- [ ] `.env` dosyasında email ayarları doğru mu?

### 5. Cloudinary Ayarları (Medya Dosyaları)
- [ ] Cloudinary hesabı oluşturdunuz mu?
- [ ] Cloud name, API key, API secret aldınız mı?
- [ ] `.env` dosyasına Cloudinary bilgilerini eklediniz mi?

### 6. PythonAnywhere Web App Ayarları
- [ ] Web app oluşturdunuz mu? (Manual configuration)
- [ ] Python version seçtiniz mi? (3.10+)
- [ ] Virtualenv path'i ayarladınız mı?
- [ ] WSGI configuration file'ı düzenlediniz mi?
- [ ] WSGI dosyasında `USERNAME` değişkenini değiştirdiniz mi?
- [ ] Static files path'lerini ayarladınız mı?

### 7. Komutları Çalıştırma
```bash
cd ~/asdasdasdasdasdqd/core
source ~/.virtualenvs/django_env/bin/activate

# Paketleri yükle
pip install -r requirements-pythonanywhere.txt

# MySQL kullanıyorsanız
pip install mysqlclient

# Migrasyonları çalıştır
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py migrate

# Superuser oluştur
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py createsuperuser

# Static dosyaları topla
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py collectstatic --noinput

# Çeviri dosyalarını derle
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py compilemessages
```

### 8. Web App Reload
- [ ] Web tab'da "Reload" butonuna bastınız mı?

### 9. Test
- [ ] Ana sayfa açılıyor mu?
- [ ] Admin paneline giriş yapabiliyor musunuz?
- [ ] Static dosyalar yükleniyor mu?
- [ ] Medya dosyaları (Cloudinary) çalışıyor mu?
- [ ] Form gönderimi çalışıyor mu?
- [ ] Email gönderimi çalışıyor mu?

### 10. Güvenlik
- [ ] `DEBUG=False` kontrol ettiniz mi?
- [ ] SECRET_KEY güçlü mü?
- [ ] Admin URL'i değiştirildi mi?
- [ ] HTTPS zorlaması aktif mi?
- [ ] CSRF koruması çalışıyor mu?

## 🔧 Sık Karşılaşılan Hatalar

### ImportError: No module named 'django'
**Çözüm:** Virtual environment doğru ayarlanmamış
```bash
# WSGI dosyasında virtualenv yolunu kontrol edin
# Web tab'da Virtualenv ayarını kontrol edin
```

### DisallowedHost at /
**Çözüm:**
```bash
# .env dosyasında
ALLOWED_HOSTS=kullaniciadi.pythonanywhere.com
```

### Static files yüklenmiyor
**Çözüm:**
```bash
# collectstatic çalıştırın
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py collectstatic --noinput

# Web tab'da Static files yollarını kontrol edin
# URL: /static/
# Directory: /home/kullaniciadi/asdasdasdasdasdqd/core/staticfiles/
```

### Database connection error (MySQL)
**Çözüm:**
```bash
# .env dosyasında kontrol edin:
# - DB_NAME doğru mu? (kullaniciadi$db_adi formatında)
# - DB_HOST doğru mu? (kullaniciadi.mysql.pythonanywhere-services.com)
# - DB_PASSWORD doğru mu?
# - mysqlclient yüklü mü?
```

### 500 Internal Server Error
**Çözüm:**
```bash
# Error log'u kontrol edin
tail -50 /var/log/kullaniciadi.pythonanywhere.com.error.log

# Veya geçici olarak DEBUG=True yapıp hatayı görün
# (Sonra mutlaka False'a çevirin!)
```

## 📝 Notlar

1. **Ücretsiz Hesap Limitleri:**
   - 1 web app
   - 512MB disk alanı
   - Günlük CPU limiti var
   - Redis/PostgreSQL yok (paid plan gerekli)

2. **Güncellemeler:**
```bash
cd ~/asdasdasdasdasdqd
git pull origin main
cd core
source ~/.virtualenvs/django_env/bin/activate
pip install -r requirements-pythonanywhere.txt
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py migrate
DJANGO_SETTINGS_MODULE=core.settings.production python manage.py collectstatic --noinput
# Web tab'dan Reload
```

3. **Backup:**
```bash
# SQLite
cp ~/asdasdasdasdasdqd/core/db.sqlite3 ~/backups/db_$(date +%Y%m%d).sqlite3

# MySQL
mysqldump -u kullaniciadi -h kullaniciadi.mysql.pythonanywhere-services.com \
  -p kullaniciadi\$veritabani_adi > ~/backups/db_$(date +%Y%m%d).sql
```

## 🎯 Sonraki Adımlar

Deploy tamamlandıktan sonra:
1. [ ] Performance testi yapın
2. [ ] Tüm sayfaları test edin
3. [ ] Email gönderimini test edin
4. [ ] Form gönderimlerini test edin
5. [ ] Admin panelini test edin
6. [ ] Mobile responsive'lik kontrol edin
7. [ ] SEO ayarlarını kontrol edin
8. [ ] Analytics ekleyin (Google Analytics)
9. [ ] Sitemap.xml'i kontrol edin
10. [ ] robots.txt'i kontrol edin

## 🔗 Faydalı Linkler

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [PythonAnywhere Forums](https://www.pythonanywhere.com/forums/)

---

**Başarılar! 🚀**
