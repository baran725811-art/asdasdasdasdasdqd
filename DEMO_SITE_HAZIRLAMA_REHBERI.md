# 🌐 DEMO SİTE HAZIRLAMA REHBERİ

**Amaç:** Potansiyel müşterilere canlı demo göstermek
**Platform:** Heroku / PythonAnywhere / Railway.app
**Tahmini Süre:** 3-4 saat

---

## 📋 DEMO SİTE GEREKSİNİMLERİ

### Temel Özellikler:
```
✅ Çalışır durumda olmalı (404 yok!)
✅ Demo verileriyle dolu (boş değil)
✅ Responsive (mobil uyumlu)
✅ Hızlı yükleme (<2 saniye)
✅ Güvenli (HTTPS)
✅ Admin panel erişimi (demo kullanıcı)
```

---

## 🚀 ADIM ADIM KURULUM

### ADIM 1: Demo Verileri Hazırlama

#### 1.1. Kategoriler Oluştur (5-8 adet)
```python
# management/commands/create_demo_data.py
from products.models import Category

categories = [
    {
        'name': 'Elektronik',
        'description': 'Akıllı telefonlar, bilgisayarlar ve elektronik ürünler',
        'meta_title': 'Elektronik Ürünler | Demo Store',
        'meta_description': 'En yeni elektronik ürünleri keşfedin',
    },
    {
        'name': 'Giyim',
        'description': 'Kadın, erkek ve çocuk giyim ürünleri',
        'meta_title': 'Giyim & Moda | Demo Store',
        'meta_description': 'Trend giyim ürünleri uygun fiyatlarla',
    },
    {
        'name': 'Ev & Yaşam',
        'description': 'Ev dekorasyonu ve yaşam ürünleri',
        'meta_title': 'Ev & Yaşam Ürünleri | Demo Store',
        'meta_description': 'Evinizi güzelleştirin',
    },
    {
        'name': 'Kozmetik',
        'description': 'Cilt bakımı ve güzellik ürünleri',
        'meta_title': 'Kozmetik & Bakım | Demo Store',
        'meta_description': 'Güzelliğiniz için en iyi ürünler',
    },
    {
        'name': 'Spor & Outdoor',
        'description': 'Spor ekipmanları ve outdoor ürünler',
        'meta_title': 'Spor Malzemeleri | Demo Store',
        'meta_description': 'Aktif yaşam için spor ürünleri',
    },
]

for cat_data in categories:
    Category.objects.create(**cat_data)
```

#### 1.2. Ürünler Oluştur (15-25 adet)
```python
from products.models import Product, Category
from decimal import Decimal

products = [
    # Elektronik
    {
        'category': Category.objects.get(name='Elektronik'),
        'name': 'iPhone 15 Pro Max',
        'short_description': 'En yeni iPhone modeli, 256GB',
        'description': 'A17 Pro çip, ProMotion ekran, titanyum kasa',
        'price': Decimal('45999.99'),
        'discount_price': Decimal('42999.99'),
        'stock': 25,
        'brand': 'Apple',
        'is_featured': True,
        'meta_title': 'iPhone 15 Pro Max 256GB | Demo Store',
        'meta_description': 'iPhone 15 Pro Max en uygun fiyatlarla',
    },
    {
        'category': Category.objects.get(name='Elektronik'),
        'name': 'Samsung Galaxy S24 Ultra',
        'short_description': 'Güçlü Android telefon',
        'description': 'Snapdragon 8 Gen 3, 200MP kamera',
        'price': Decimal('38999.99'),
        'stock': 18,
        'brand': 'Samsung',
        'is_featured': True,
    },
    {
        'category': Category.objects.get(name='Elektronik'),
        'name': 'MacBook Air M3',
        'short_description': '13 inç, 16GB RAM, 512GB SSD',
        'description': 'Yeni M3 çip ile maksimum performans',
        'price': Decimal('55999.99'),
        'discount_price': Decimal('52999.99'),
        'stock': 12,
        'brand': 'Apple',
        'is_featured': False,
    },

    # Giyim
    {
        'category': Category.objects.get(name='Giyim'),
        'name': 'Kadın Triko Kazak',
        'short_description': 'Yumuşak, sıcak, rahat',
        'description': 'Premium pamuklu triko kazak',
        'price': Decimal('299.99'),
        'discount_price': Decimal('199.99'),
        'stock': 50,
        'brand': 'Zara',
    },
    {
        'category': Category.objects.get(name='Giyim'),
        'name': 'Erkek Slim Fit Kot Pantolon',
        'short_description': 'Modern kesim, rahat kumaş',
        'description': 'Streç kumaşlı, koyu mavi kot pantolon',
        'price': Decimal('399.99'),
        'stock': 35,
        'brand': 'Levis',
    },

    # Ev & Yaşam
    {
        'category': Category.objects.get(name='Ev & Yaşam'),
        'name': 'Robot Süpürge',
        'short_description': 'Akıllı navigasyon sistemi',
        'description': 'WiFi bağlantılı, app kontrollü robot süpürge',
        'price': Decimal('4999.99'),
        'discount_price': Decimal('3999.99'),
        'stock': 15,
        'brand': 'Xiaomi',
        'is_featured': True,
    },

    # Kozmetik
    {
        'category': Category.objects.get(name='Kozmetik'),
        'name': 'Nemlendirici Krem 50ml',
        'short_description': 'Her cilt tipi için',
        'description': 'Hyaluronik asit içerikli yoğun nemlendirici',
        'price': Decimal('249.99'),
        'stock': 100,
        'brand': 'CeraVe',
    },

    # Spor
    {
        'category': Category.objects.get(name='Spor & Outdoor'),
        'name': 'Yoga Matı Premium',
        'short_description': '6mm kalınlık, kaymaz',
        'description': 'Çevre dostu malzemeden yoga matı',
        'price': Decimal('299.99'),
        'discount_price': Decimal('249.99'),
        'stock': 40,
        'brand': 'Nike',
    },
]

for prod_data in products:
    Product.objects.create(**prod_data)
```

#### 1.3. Carousel Slaytlar (3-5 adet)
```python
from home.models import CarouselSlide

slides = [
    {
        'title': 'Yeni Sezon İndirimleri',
        'description': 'Tüm ürünlerde %50\'ye varan indirimler!',
        'button_text': 'Hemen Alışverişe Başla',
        'button_url': '/products/',
        'order': 1,
        'is_active': True,
    },
    {
        'title': 'Ücretsiz Kargo',
        'description': '500 TL ve üzeri alışverişlerde kargo bizden',
        'button_text': 'Detaylı Bilgi',
        'button_url': '/about/',
        'order': 2,
        'is_active': True,
    },
    {
        'title': 'En Yeni Ürünler',
        'description': 'Son çıkan ürünleri keşfedin',
        'button_text': 'Keşfet',
        'button_url': '/products/',
        'order': 3,
        'is_active': True,
    },
]

for slide_data in slides:
    CarouselSlide.objects.create(**slide_data)
```

#### 1.4. Hakkımızda & Hizmetler
```python
from about.models import About, Service

# Hakkımızda
About.objects.create(
    title='Demo Store',
    short_description='2020 yılından beri kaliteli ürünler',
    mission='Müşterilerimize en iyi alışveriş deneyimini sunmak',
    vision='Türkiye\'nin en güvenilir online mağazası olmak',
    story='2020 yılında küçük bir ekiple başladık...',
    years_experience=4,
    completed_jobs=5000,
    happy_customers=12000,
    total_services=8,
)

# Hizmetler
services = [
    {
        'title': 'Hızlı Teslimat',
        'description': 'Siparişleriniz 24 saat içinde kargoda',
    },
    {
        'title': 'Güvenli Ödeme',
        'description': 'SSL sertifikalı güvenli ödeme altyapısı',
    },
    {
        'title': '7/24 Destek',
        'description': 'Müşteri hizmetlerimiz her zaman yanınızda',
    },
    {
        'title': 'Kolay İade',
        'description': '14 gün içinde ücretsiz iade hakkı',
    },
]

for i, service_data in enumerate(services, 1):
    service_data['order'] = i
    Service.objects.create(**service_data)
```

#### 1.5. Management Command Oluştur
```bash
# core/management/commands/create_demo_data.py
python manage.py create_demo_data
```

---

### ADIM 2: Görseller Hazırlama

#### 2.1. Ücretsiz Görsel Kaynakları:
```
📸 Unsplash.com - Yüksek kalite, ücretsiz
📸 Pexels.com - Çok çeşitli görseller
📸 Pixabay.com - Telif hakkı yok
📸 Freepik.com - Vektör + fotoğraf (bazıları premium)
```

#### 2.2. Görsel İsimlendirme:
```
✅ İyi: iphone-15-pro-max-1.jpg
❌ Kötü: IMG_1234.jpg

✅ İyi: carousel-yeni-sezon.jpg
❌ Kötü: photo.jpg
```

#### 2.3. Görsel Boyutları:
```
Carousel: 1920x1080 (landscape)
Ürün (ana): 800x800 (square)
Ürün (thumbnail): 300x300 (square)
Kategori: 600x400 (landscape)
```

#### 2.4. Cloudinary'ye Yükleme:
```python
# Admin panelden manuel yükleme
# veya script ile:

from cloudinary.uploader import upload

images = {
    'products/iphone-15.jpg': 'path/to/iphone.jpg',
    'products/samsung-s24.jpg': 'path/to/samsung.jpg',
}

for public_id, file_path in images.items():
    upload(file_path, public_id=public_id)
```

---

### ADIM 3: Deployment (Heroku)

#### 3.1. Gerekli Dosyalar:

**requirements.txt** (zaten var)

**Procfile:**
```
web: gunicorn core.wsgi --log-file -
release: python manage.py migrate
```

**runtime.txt:**
```
python-3.12.1
```

**requirements.txt'e ekle:**
```
gunicorn==21.2.0
dj-database-url==2.1.0
whitenoise==6.6.0
psycopg2-binary==2.9.10
```

#### 3.2. Settings Güncellemeleri:

**core/settings.py:**
```python
import dj_database_url

# Heroku için
if 'DYNO' in os.environ:
    DEBUG = False
    ALLOWED_HOSTS = ['your-app.herokuapp.com']

    # Database
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )

    # Static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 3.3. Heroku Deployment:
```bash
# Heroku CLI kur (tek seferlik)
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew tap heroku/brew && brew install heroku

# Login
heroku login

# Yeni app oluştur
heroku create demo-ecommerce-tr

# PostgreSQL ekle
heroku addons:create heroku-postgresql:mini

# Redis ekle (opsiyonel)
heroku addons:create heroku-redis:mini

# Environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set CLOUDINARY_CLOUD_NAME="your-cloud"
heroku config:set CLOUDINARY_API_KEY="your-key"
heroku config:set CLOUDINARY_API_SECRET="your-secret"

# Deploy
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# Migrate
heroku run python manage.py migrate

# Demo data oluştur
heroku run python manage.py create_demo_data

# Superuser oluştur
heroku run python manage.py createsuperuser

# Açık
heroku open
```

---

### ADIM 4: PythonAnywhere (Alternatif)

Daha kolay ama biraz daha yavaş:

#### 4.1. Hesap Oluştur:
```
🌐 www.pythonanywhere.com
✅ Free tier yeterli (ilk demo için)
```

#### 4.2. Adımlar:
```
1. "Web" sekmesine git
2. "Add a new web app" tıkla
3. Django seç
4. Python 3.12 seç
5. Proje adı: demo_ecommerce

6. Upload code:
   - Bash console aç
   - git clone [your-repo]
   - cd [your-repo]
   - pip install -r requirements.txt

7. Database setup:
   - SQLite yeterli (demo için)
   - python manage.py migrate
   - python manage.py create_demo_data

8. Static files:
   - python manage.py collectstatic

9. WSGI config düzenle:
   - Web sekmesinden WSGI file linki
   - Path'leri düzelt

10. Reload web app

11. Test: yourusername.pythonanywhere.com
```

---

### ADIM 5: Domain & SSL

#### 5.1. Ücretsiz Domain (Demo İçin):
```
✅ Heroku: app-name.herokuapp.com
✅ PythonAnywhere: username.pythonanywhere.com
✅ Railway.app: app-name.railway.app
✅ Render.com: app-name.onrender.com
```

#### 5.2. Özel Domain (Profesyonel):
```
💰 .com.tr domain: ~100 TL/yıl
💰 .com domain: ~150 TL/yıl

Nereden: GoDaddy, Namecheap, Natro
```

#### 5.3. SSL:
```
✅ Heroku: Otomatik HTTPS
✅ PythonAnywhere: Otomatik HTTPS
✅ Let's Encrypt: Ücretsiz (kendi sunucuda)
```

---

### ADIM 6: Demo Admin Kullanıcısı

```python
# Güvenli demo kullanıcısı oluştur
python manage.py shell

from django.contrib.auth.models import User

# Demo admin
User.objects.create_superuser(
    username='demo',
    email='demo@example.com',
    password='Demo123!@#'
)

# Demo müşteri
User.objects.create_user(
    username='musteri',
    email='musteri@example.com',
    password='Musteri123!'
)
```

**Demo sayfasına not ekle:**
```
🔑 Admin Girişi:
   Kullanıcı: demo
   Şifre: Demo123!@#

   Admin Panel: /admin/
```

---

### ADIM 7: SEO & Meta Tags

```html
<!-- templates/base.html -->
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO -->
    <title>{% block title %}Demo E-Ticaret | Modern Django Platform{% endblock %}</title>
    <meta name="description" content="{% block description %}Profesyonel Django e-ticaret demo sitesi{% endblock %}">
    <meta name="keywords" content="django, e-ticaret, demo, online mağaza">

    <!-- Open Graph (LinkedIn, Facebook) -->
    <meta property="og:title" content="Django E-Ticaret Demo">
    <meta property="og:description" content="Modern ve hızlı e-ticaret platformu">
    <meta property="og:image" content="{{ STATIC_URL }}images/og-image.jpg">
    <meta property="og:url" content="{{ request.build_absolute_uri }}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Django E-Ticaret Demo">
    <meta name="twitter:description" content="Modern ve hızlı e-ticaret platformu">

    <!-- Favicon -->
    <link rel="icon" type="image/png" href="{{ STATIC_URL }}favicon.png">
</head>
```

---

### ADIM 8: Performans Optimizasyonu

#### 8.1. Caching Aktif Et:
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,
    }
}

# View'lerde cache kullan
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 dakika
def product_list(request):
    ...
```

#### 8.2. Lazy Loading:
```html
<!-- templates/products/product_card.html -->
<img src="{{ product.cropped_image.url }}"
     loading="lazy"
     alt="{{ product.alt_text }}">
```

#### 8.3. Minify CSS/JS:
```python
# settings.py
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
```

---

### ADIM 9: Test & QA

#### Kontrol Listesi:
```
□ Anasayfa yükleniyor mu?
□ Tüm linkler çalışıyor mu?
□ Ürün detay sayfaları açılıyor mu?
□ Sepet fonksiyonu çalışıyor mu?
□ Admin paneline giriş yapılıyor mu?
□ Mobilde düzgün görünüyor mu?
□ Görseller yükleniyor mu?
□ 404 sayfası var mı?
□ Hata sayfası (500) var mı?
□ SSL aktif mi (HTTPS)?
□ Sayfa yükleme hızı <2 sn mi?
□ Tüm formlar çalışıyor mu?
□ Email gönderimi test edildi mi?
```

#### Test Araçları:
```
🔍 Google PageSpeed Insights
   - Performans skoru: >85

🔍 GTmetrix
   - Grade: A veya B

🔍 Mobile-Friendly Test (Google)
   - Mobile-friendly: Yes

🔍 SSL Labs
   - SSL Rating: A
```

---

### ADIM 10: Monitoring & Analytics

#### 10.1. Google Analytics:
```html
<!-- templates/base.html -->
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

#### 10.2. Uptime Monitoring:
```
🔔 UptimeRobot (ücretsiz)
   - 5 dakikada bir check
   - Email alert

🔔 StatusCake
   - Uptime monitoring
   - Performance monitoring
```

---

## 📦 DEMO PAKETİ (Müşteriye Gösterilecek)

### Hazır Olması Gerekenler:

1. **Canlı Site**
   - URL: demo-yourbrand.herokuapp.com
   - Admin: /admin/ (demo/Demo123!@#)

2. **Ekran Görüntüleri** (10 adet)
   - Anasayfa (desktop)
   - Anasayfa (mobil)
   - Ürün listesi
   - Ürün detay
   - Sepet
   - Admin paneli
   - Galeri
   - Hakkımızda
   - İletişim
   - Checkout

3. **Video Demo** (2-3 dk)
   - Screen recording
   - Voiceover (Türkçe)
   - YouTube'a yükle

4. **PDF Döküman**
   - Özellikler listesi
   - Teknoloji stack
   - Admin kullanım kılavuzu

---

## ⚡ HIZLI KURULUM (1 Saat)

Zaman yoksa minimal demo:

```bash
# 1. Heroku'ya deploy (15 dk)
heroku create demo-ecommerce-quick
git push heroku main

# 2. Minimal demo data (10 dk)
heroku run python manage.py shell
# 3 kategori, 10 ürün, 2 slider yarat

# 3. Test (5 dk)
# Tüm sayfaları kontrol et

# 4. Görseller (30 dk)
# Unsplash'tan 10 görsel indir
# Cloudinary'e yükle
# Ürünlere ata

TOPLAM: ~1 saat
```

---

## ✅ SON KONTROL

Demo yayına almadan önce:

```
✅ Tüm sayfalarda "Demo" yazdığından emin ol
✅ Gerçek firma bilgileri kullanma
✅ Test email adresleri kullan
✅ Gerçek ödeme entegrasyonu YOK (sadece UI)
✅ Gizli bilgiler (secret key, vs.) güvende
✅ Error logging aktif
✅ Admin paneline kolay erişim
✅ Müşteriye demo credentials ver
```

---

## 🎁 BONUS: Demo Announcement

LinkedIn/Instagram paylaşımı:

```
🚀 Yeni Demo Sitemiz Yayında!

Modern Django e-ticaret platformumuzu keşfedin:
🔗 demo-yourbrand.herokuapp.com

✨ Özellikler:
• Lightning-fast performance
• Bank-level security
• Mobile-optimized
• SEO-ready
• Multi-language support

👉 Admin paneline giriş yapın ve kendiniz test edin:
   Kullanıcı: demo
   Şifre: Demo123!@#

💬 Projeniz için teklif almak ister misiniz?
   DM'den veya email'den ulaşın!

#django #eticaret #webgeliştirme #startup
```

---

**Demo siteniz hazır! Artık müşterilere gösterebilirsiniz! 🎉**

*Hazırlayan: Claude AI*
*Tarih: 2 Ocak 2026*
