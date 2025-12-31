# Django Web Uygulaması

Modern, güvenli ve çok dilli Django web uygulaması.

## 🌟 Özellikler

- ✅ Çok dilli destek (TR, EN, DE, FR, AR, RU)
- ✅ Admin dashboard
- ✅ Ürün yönetimi
- ✅ Galeri sistemi
- ✅ İletişim formu
- ✅ SEO optimizasyonu
- ✅ Cloudinary entegrasyonu
- ✅ Güvenlik özellikleri (Rate limiting, CAPTCHA, Axes)

## 🚀 Deployment

### PythonAnywhere'e Deploy (Ücretsiz)

Detaylı adım adım talimatlar için:
👉 **[PYTHONANYWHERE_DEPLOYMENT.md](./PYTHONANYWHERE_DEPLOYMENT.md)** dosyasına bakın

Kısa özet:
1. PythonAnywhere hesabı oluşturun (ücretsiz)
2. Projeyi klonlayın
3. Virtual environment kurun
4. Dependencies yükleyin
5. .env dosyasını yapılandırın
6. Migration çalıştırın
7. Web app oluşturun
8. WSGI dosyasını ayarlayın
9. Yayına alın!

### Yerel Geliştirme

```bash
# Projeyi klonlayın
git clone https://github.com/baran725811-art/asdasdasdasdasdqd.git
cd asdasdasdasdasdqd/core

# Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies yükleyin
pip install -r requirements.txt

# .env dosyası oluşturun
cp .env.example .env
# .env dosyasını düzenleyin

# Migration çalıştırın
python manage.py migrate

# Superuser oluşturun
python manage.py createsuperuser

# Sunucuyu başlatın
python manage.py runserver
```

## 📋 Gereksinimler

- Python 3.10+
- Django 5.2+
- PostgreSQL (production) / SQLite (development)
- Cloudinary hesabı (resim storage için)

## 🔧 Teknolojiler

- **Framework:** Django 5.2
- **Database:** PostgreSQL / SQLite
- **Storage:** Cloudinary
- **Frontend:** HTML, CSS, JavaScript
- **Security:** django-axes, django-simple-captcha
- **i18n:** django-modeltranslation, DeepL API

## 📝 Lisans

Bu proje özel kullanım içindir.

## 🆘 Yardım

Sorularınız için:
- Issue açın: https://github.com/baran725811-art/asdasdasdasdasdqd/issues
- Deployment rehberi: [PYTHONANYWHERE_DEPLOYMENT.md](./PYTHONANYWHERE_DEPLOYMENT.md)
