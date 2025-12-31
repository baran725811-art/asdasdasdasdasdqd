# Django Multi-Language E-Commerce Platform

Modern, güvenli ve çok dilli Django tabanlı e-ticaret platformu.

## ✨ Özellikler

### 🌍 Çok Dilli Destek
- 6 dil desteği: Türkçe, İngilizce, Almanca, Fransızca, Arapça, Rusça
- Django Modeltranslation ile otomatik çeviri yönetimi
- DeepL API entegrasyonu ile otomatik çeviri

### 🔒 Güvenlik
- Django Axes - Brute force koruması
- CAPTCHA entegrasyonu
- Argon2 password hashing
- CSRF, XSS, Clickjacking koruması
- Rate limiting
- Güvenli session yönetimi
- Security headers middleware

### 📸 Medya Yönetimi
- Cloudinary entegrasyonu
- Otomatik resim optimizasyonu
- ImageKit ile çoklu format desteği
- Lazy loading

### 🎨 UI/UX
- Modern responsive tasarım
- CKEditor 5 entegrasyonu
- Bootstrap 5
- Dinamik breadcrumb
- SEO optimizasyonu

### 📊 Dashboard
- Gelişmiş admin paneli
- Çoklu dil yönetimi
- İçerik yönetimi
- İstatistik takibi

## 🚀 Kurulum

### Gereksinimler
- Python 3.10+
- Django 5.2.4
- PostgreSQL veya SQLite (development için)

### Yerel Geliştirme

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/baran725811-art/asdasdasdasdasdqd.git
cd asdasdasdasdasdqd/core
```

2. **Virtual environment oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. **Paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Environment variables ayarlayın:**
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

5. **Veritabanı migration:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Static dosyaları toplayın:**
```bash
python manage.py collectstatic
```

7. **Geliştirme sunucusunu başlatın:**
```bash
python manage.py runserver
```

## 🌐 PythonAnywhere Deployment

Detaylı deployment rehberi için: **[PYTHONANYWHERE_DEPLOYMENT.md](PYTHONANYWHERE_DEPLOYMENT.md)**

### Hızlı Başlangıç

1. PythonAnywhere'de Bash console açın
2. Projeyi klonlayın
3. Virtual environment oluşturun
4. `.env` dosyasını yapılandırın
5. Migration ve collectstatic çalıştırın
6. WSGI dosyasını yapılandırın
7. Reload butonuna tıklayın

Detaylar için deployment dokümanına bakın.

## 📁 Proje Yapısı

```
core/
├── core/                 # Ana proje ayarları
│   ├── settings/        # Ortam bazlı ayarlar
│   │   ├── base.py     # Temel ayarlar
│   │   ├── development.py
│   │   └── production.py
│   ├── middleware.py   # Güvenlik middleware
│   ├── urls.py
│   └── wsgi.py
├── about/              # Hakkımızda app
├── contact/            # İletişim app
├── dashboard/          # Admin dashboard
├── gallery/            # Galeri app
├── home/               # Ana sayfa app
├── products/           # Ürünler app
├── reviews/            # Yorumlar app
├── static/             # Statik dosyalar
├── templates/          # Template dosyaları
├── locale/             # Çeviri dosyaları
├── deployment/         # Deployment dosyaları
│   └── pythonanywhere_wsgi.py
└── manage.py
```

## 🔧 Konfigürasyon

### Environment Variables (.env)

```bash
# Django
DJANGO_ENV=production|development
DEBUG=False
SECRET_KEY=your-secret-key

# Database
DB_ENGINE=sqlite3|mysql
DB_NAME=
DB_USER=
DB_PASSWORD=

# Security
ALLOWED_HOSTS=domain.com,www.domain.com
CSRF_TRUSTED_ORIGINS=https://domain.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Admin
ADMIN_URL=custom-admin-url/
```

## 🛡️ Güvenlik

### Üretim Öncesi Checklist

- [ ] `DEBUG=False`
- [ ] Güçlü `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` düzenlendi
- [ ] HTTPS aktif
- [ ] Admin URL değiştirildi
- [ ] CSRF koruması aktif
- [ ] Rate limiting aktif
- [ ] Security headers aktif
- [ ] Log monitoring aktif

### Güvenlik Özellikleri

- **Brute Force Protection:** Django Axes
- **Rate Limiting:** django-ratelimit
- **CAPTCHA:** django-simple-captcha
- **Password Hashing:** Argon2
- **CSRF Protection:** Django built-in
- **XSS Protection:** Security headers
- **SQL Injection:** Django ORM
- **Clickjacking:** X-Frame-Options

## 📊 Performans

### Cache Stratejisi
- File-based cache (PythonAnywhere)
- Template caching
- Static files optimization
- Django Compressor

### Optimizasyonlar
- Lazy loading
- Image optimization (Cloudinary)
- Minification (CSS, JS)
- GZIP compression

## 🌍 Çoklu Dil

### Desteklenen Diller
- 🇹🇷 Türkçe (Varsayılan)
- 🇬🇧 İngilizce
- 🇩🇪 Almanca
- 🇫🇷 Fransızca
- 🇸🇦 Arapça
- 🇷🇺 Rusça

### Çeviri Yönetimi

```bash
# Yeni çeviri dosyaları oluştur
python manage.py makemessages -l en

# Çevirileri derle
python manage.py compilemessages
```

## 📝 Lisans

Bu proje özel kullanım içindir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'e push yapın (`git push origin feature/amazing`)
5. Pull Request oluşturun

## 📞 İletişim

Proje Sahibi: [GitHub](https://github.com/baran725811-art)

## 🙏 Teşekkürler

- Django Team
- Cloudinary
- PythonAnywhere
- Tüm açık kaynak katkıcıları

---

**Made with ❤️ using Django**
