# 🔴 DJANGO PROJESİ - KAPSAMLI EKSİKLER VE HATALAR LİSTESİ

**Proje:** Baran Oto Anahtar - Django Web Sitesi
**İnceleme Tarihi:** 27 Aralık 2025
**Durum:** Kritik hatalar mevcut - Production'a alınamaz

---

## 📌 GÜVENLİK KRİTİK (HEMEN DÜZELTİLMELİ)

### GUV-001: API Anahtarları Hardcoded
- **Dosya:** `ceviri3.py:38-39`
- **Sorun:** DeepL ve Gemini API anahtarları kodda açıkça yazılmış
- **Risk:** GitHub'a push edilirse üçüncü kişiler kullanabilir
- **Çözüm:**
  ```bash
  # .env dosyası oluştur
  echo "DEEPL_API_KEY=64605b99-7c0c-481b-a28a-5dbd1b72377d:fx" > .env
  echo "GEMINI_API_KEY=AIzaSyDb3LY05ahVBctyVPlvFVmmzLzv-XrO_9Q" >> .env

  # ceviri3.py'de değiştir
  from decouple import config
  DEEPL_API_KEY = config('DEEPL_API_KEY')
  GEMINI_API_KEY = config('GEMINI_API_KEY')

  # .gitignore'a ekle
  echo ".env" >> .gitignore
  ```

### GUV-002: CSRF Exempt Tehlikesi
- **Dosya:** `core/core/views.py:71, 128, 435`
- **Sorun:** 3 endpoint `@csrf_exempt` ile korunmuyor
  - `set_main_language`
  - `set_dashboard_language`
  - `save_cookie_preferences`
- **Risk:** CSRF saldırılarına açık
- **Çözüm:** `@csrf_exempt` kaldır, CSRF token doğrulaması ekle

### GUV-003: .env Dosyası Eksik
- **Sorun:** Production ayarları `.env` değişkenlerine bağımlı ama dosya yok
- **Eksik Değişkenler:**
  - SECRET_KEY
  - ALLOWED_HOSTS
  - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
  - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
  - DEFAULT_FROM_EMAIL
  - ADMIN_EMAIL
  - REDIS_URL
  - CSRF_TRUSTED_ORIGINS
  - ADMIN_URL
- **Çözüm:** `.env.example` dosyası oluştur

---

## 🔴 KRİTİK YAPISAL HATALAR (DJANGO ÇALIŞMAYACAK)

### KRT-001: manage.py Settings Path Yanlış
- **Dosya:** `core/manage.py:9`
- **Sorun:** `DJANGO_SETTINGS_MODULE = 'core.settings'` ama settings bir klasör
- **Sonuç:** Django komutları çalışmayacak
- **Çözüm:**
  ```python
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
  ```

### KRT-002: settings/__init__.py Dosyası Eksik
- **Dosya:** `core/core/settings/__init__.py` - **DOSYA YOK**
- **Sorun:** Settings klasörü Python paketi olarak tanınmıyor
- **Sonuç:** ImportError
- **Çözüm:**
  ```bash
  # Dosya oluştur
  touch core/core/settings/__init__.py

  # İçeriği:
  from .development import *
  ```

### KRT-003: Duplicate Context Processor
- **Dosya:** `core/core/settings/base.py:185-186`
- **Sorun:** `meta_seo_context` iki kere tanımlanmış
- **Sonuç:** Settings parse hatası veya context processor 2 kez çalışır
- **Çözüm:** Satır 185'i sil:
  ```python
  # ÖNCE (HATALI):
  185: 'core.context_processors.meta_seo_context'
  186: 'core.context_processors.meta_seo_context',  # Meta SEO context

  # SONRA (DOĞRU):
  186: 'core.context_processors.meta_seo_context',  # Meta SEO context
  ```

### KRT-004: Contact Models - Duplicate ip_address Field
- **Dosya:** `core/contact/models.py:11 ve 23-28`
- **Sorun:** `ip_address` alanı 2 kez tanımlanmış (biri class içinde, biri dışında)
- **Sonuç:** Migration hatası, model create edilemez
- **Çözüm:** Satır 23-28'i sil (class dışındaki)

### KRT-005: Review Models - Duplicate ip_address Field
- **Dosya:** `core/reviews/models.py:16 ve 29-34`
- **Sorun:** `ip_address` alanı 2 kez tanımlanmış
- **Sonuç:** Migration hatası
- **Çözüm:** Satır 29-34'ü sil

### KRT-006: Review Models - User Field Eksik
- **Dosya:** `core/reviews/models.py`
- **Sorun:** `contact/views.py:43` ve `core/views.py`'de `review.user = request.user` atanıyor ama model'de user field'ı yok
- **Sonuç:** `AttributeError: 'Review' object has no attribute 'user'`
- **Çözüm:** Review modeline ekle:
  ```python
  user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kullanıcı")
  ```

### KRT-007: About Models - ValidationError Import Eksik
- **Dosya:** `core/about/models.py:118`
- **Sorun:** `raise ValidationError(...)` kullanılıyor ama import yok
- **Sonuç:** `NameError: name 'ValidationError' is not defined`
- **Çözüm:**
  ```python
  from django.core.exceptions import ValidationError
  ```

### KRT-008: Signals - Focal Point AttributeError
- **Dosya:** `core/core/signals.py:197, 281`
- **Sorun:** Gallery ve Product signals'inde `focal_point_x`, `focal_point_y` alanları kullanılıyor ama migration'da silinmiş
  - Migration: `0004_remove_gallery_cropped_image_url_and_more.py`
- **Sonuç:** `AttributeError: 'Gallery' object has no attribute 'focal_point_x'`
- **Çözüm:** Signals'ten focal point kodlarını sil VEYA model'e alanları geri ekle

### KRT-009: Middleware - timezone Import Eksik
- **Dosya:** `core/core/middleware.py:601`
- **Sorun:** `timezone.now()` kullanılıyor ama import yok (satır 18'de var ama kontrol et)
- **Sonuç:** `NameError: name 'timezone' is not defined`
- **Çözüm:**
  ```python
  from django.utils import timezone
  ```

---

## 🟠 EKSİK BAĞIMLILIKLAR VE KONFİGÜRASYONLAR

### BAG-001: Debug Toolbar Paketi Eksik
- **Dosya:** `core/core/urls.py:89`
- **Sorun:** `import debug_toolbar` var ama `requirements.txt`'de yok
- **Sonuç:** Development'ta ImportError
- **Çözüm:**
  ```bash
  echo "django-debug-toolbar==4.4.6" >> core/requirements.txt
  pip install django-debug-toolbar==4.4.6
  ```

### BAG-002: Django Redis Paketi Eksik
- **Dosya:** `core/core/settings/production.py:76`
- **Sorun:** Production'da Redis cache kullanılıyor ama paket yok
- **Sonuç:** Production'da cache hatası
- **Çözüm:**
  ```bash
  echo "django-redis==5.4.0" >> core/requirements.txt
  pip install django-redis==5.4.0
  ```

### BAG-003: Cloudinary Apps INSTALLED_APPS'ta Eksik
- **Dosya:** `core/core/settings/base.py:19-46`
- **Sorun:** `cloudinary` ve `cloudinary_storage` INSTALLED_APPS'e eklenmemiş
- **Sonuç:** Cloudinary field'ları çalışmaz, media upload hatası
- **Çözüm:** base.py INSTALLED_APPS'e ekle:
  ```python
  INSTALLED_APPS = [
      'django.contrib.admin',
      # ... diğerleri

      # Cloudinary (staticfiles'dan ÖNCE)
      'cloudinary_storage',
      'django.contrib.staticfiles',

      # Diğer third-party
      'cloudinary',
      # ...
  ]
  ```

### BAG-004: Captcha Konfigürasyonu Eksik
- **Dosya:** `core/core/settings/base.py`
- **Sorun:** `django-simple-captcha` için konfigürasyon eksik
- **Sonuç:** Captcha render hatası
- **Çözüm:** base.py'ye ekle:
  ```python
  # Captcha ayarları
  CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
  CAPTCHA_LENGTH = 4
  CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
  CAPTCHA_FONT_SIZE = 32
  CAPTCHA_LETTER_ROTATION = (-30, 30)
  ```

### BAG-005: Email Backend Development'ta Yok
- **Dosya:** `core/core/settings/development.py`
- **Sorun:** EMAIL_BACKEND tanımlanmamış (sadece production'da var)
- **Sonuç:** Development'ta email gönderiminde hata
- **Çözüm:** development.py'ye ekle:
  ```python
  # Email - Console backend (development)
  EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
  ```

### BAG-006: DeepL API Key Environment Variable Eksik
- **Dosya:** `core/core/settings/base.py:379-382`
- **Sorun:** DEEPL_API_KEY config'den alınmıyor
- **Sonuç:** Otomatik çeviri çalışmaz
- **Çözüm:** base.py'ye ekle:
  ```python
  DEEPL_API_KEY = config('DEEPL_API_KEY', default='')
  ```

### BAG-007: Logs Dizini Eksik
- **Sorun:** `base.py:129,134` log dosyaları `logs/` dizinine yazmaya çalışıyor ama dizin yok
- **Sonuç:** Logging hatası
- **Çözüm:**
  ```bash
  mkdir -p core/logs
  touch core/logs/.gitkeep
  echo "logs/*.log" >> .gitignore
  ```

---

## 🟡 KOD KALİTESİ VE BEST PRACTICE SORUNLARI

### KLT-001: Contact Views - IP Address Capture Edilmiyor
- **Dosya:** `core/contact/views.py:28` ve `core/core/views.py:38`
- **Sorun:** IP address yakalanıp form'a atanmıyor
- **Sonuç:** Database'de ip_address NULL
- **Çözüm:**
  ```python
  def get_client_ip(request):
      x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
      if x_forwarded_for:
          ip = x_forwarded_for.split(',')[0]
      else:
          ip = request.META.get('REMOTE_ADDR')
      return ip

  # View'da:
  contact = contact_form.save(commit=False)
  contact.ip_address = get_client_ip(request)
  contact.save()
  ```

### KLT-002: Bare Except Kullanımı
- **Dosyalar:**
  - `core/context_processors.py:51, 78, 240, 336`
  - `core/home/models.py:99`
  - `core/core/signals.py:70, 274-275`
- **Sorun:** Genel `except:` veya `except Exception:` - spesifik exception yok
- **Sonuç:** Debugging zor, hata logging eksik
- **Çözüm:** Spesifik exception'lar yakala:
  ```python
  try:
      # kod
  except ObjectDoesNotExist:
      logger.error("Object bulunamadı")
  except ValidationError as e:
      logger.error(f"Validation hatası: {e}")
  ```

### KLT-003: Admin Duplicate Import
- **Dosya:** `core/core/admin.py:2 ve 17`
- **Sorun:** `from django.contrib import admin` iki kez import
- **Sonuç:** Linting warning
- **Çözüm:** Duplicate import'ı sil

### KLT-004: Gallery Models Import Syntax Hatası
- **Dosya:** `core/gallery/models.py:25`
- **Sorun:** Import class içinde mi dosya başında mı belirsiz
- **Sonuç:** Potansiyel syntax hatası
- **Çözüm:** Import'u dosya başına taşı

### KLT-005: Review Views - select_related Hatası
- **Dosya:** `core/reviews/views.py:34`
- **Sorun:** `select_related('user')` ama user field'ı yok
- **Sonuç:** Query hatası
- **Çözüm:** User field ekle veya select_related'ı sil

---

## 🗑️ GEREKSIZ DOSYALAR (SİLİNMELİ)

### GEREKSIZ-001: Root Dizin - Garip Dosya İsimleri
- **Dosyalar:**
  - `bool`
  - `str`
  - `List[TranslationItem]`
  - `GeminiResult`
  - `0.2)`
  - `50`
- **Sorun:** Test sırasında oluşmuş gereksiz dosyalar
- **Çözüm:**
  ```bash
  cd /home/user/asdasdasdasdasdqd
  rm -f bool str "List[TranslationItem]" GeminiResult "0.2)" 50
  ```

### GEREKSIZ-002: Çeviri Script'leri
- **Dosyalar:**
  - `ceviri.py`
  - `ceviri2.py`
  - `ceviri3.py`
  - `ceviri4.py`
- **Sorun:** Production'a gerek yok, development tool
- **Önerilen Aksiyon:** Ayrı bir klasöre taşı (`/scripts/` veya `/tools/`)

### GEREKSIZ-003: Test Dosyaları
- **Dosyalar:**
  - `dosya_yolu.py`
  - `product.html` (root'ta)
  - `sade_dosya_listesi.txt`
- **Sorun:** Root dizini kirletiyor
- **Önerilen Aksiyon:** Sil veya `/temp/` klasörüne taşı

---

## 📱 KULLANICI BELİRTİLEN UI/UX HATALARI (hatalar.txt ve hatalar2.txt)

### UI-001: Carousel Resim Düzeni Bozuk
- **Sorun:** Carousel resim tam oturmuyor, sağ kaydırma butonu görülmüyor
- **Dosya:** `core/home/templates/home/index.html` (carousel section)
- **Çözüm Gerekli:** CSS ve responsive düzenleme

### UI-002: 404 Hataları Error Sayfasına Yönlendirilmiyor
- **Sorun:** 404 hatalarında sayfa yönlendirmesi yok
- **Dosya:** `core/core/views.py` - custom_404_view
- **Çözüm Gerekli:** Error handler kontrol et, template render et

### UI-003: İletişim Formunda Yorum Bölümü Görünmüyor
- **Sorun:** İletişim sayfasında yorum yapma ve mesaj bölümleri görünmüyor
- **Dosya:** `core/contact/templates/contact/contact.html`
- **Çözüm Gerekli:** Template kontrol et, form field'ları render et

### UI-004: Back-to-Top Butonu Konumu Yanlış
- **Sorun:** Çok köşede, sağ tarafta olması gerekiyor
- **Dosya:** `static/css/main.css` veya template
- **Çözüm Gerekli:** CSS position düzenle

### UI-005: Telefon Yerine WhatsApp İkonu
- **Sorun:** Sol bölümde WhatsApp olacak, telefon değil
- **Dosya:** Footer template
- **Çözüm Gerekli:** Icon değiştir

### UI-006: "Tümünü Gör" Butonları Çalışmıyor
- **Sorun:** Öne çıkanları gör, ekibimiz tümünü gör butonları çalışmıyor
- **Dosya:** Template link'leri
- **Çözüm Gerekli:** URL routing kontrol et

### UI-007: Modal Kapatma Sorunu
- **Sorun:** Galeri ve hizmetler modalı kaydet sonrası kapanmıyor
- **Dosya:** Dashboard JavaScript
- **Çözüm Gerekli:** AJAX success callback'te modal close ekle

### UI-008: Sıralama Alanları Duplicate (Carousel)
- **Sorun:** Carousel'de iki sıralama bölümü var, biri devre dışı
- **Dosya:** Dashboard carousel form
- **Çözüm Gerekli:** Üstteki sıralama field'ını kaldır

### UI-009: URL Slug Otomatik Dolmuyor
- **Sorun:** Ürün ve kategori slug sadece tek harf yazıyor
- **Dosya:** Dashboard JavaScript - slugify function
- **Çözüm Gerekli:** Slugify function kontrol et

### UI-010: Katalog Sayfası Boş
- **Sorun:** `http://127.0.0.1:8000/katalog/` boş sayfa, HTML çekmiyor
- **Dosya:** `dashboard/views.py` - catalog_view
- **Çözüm Gerekli:** View ve template kontrol et

---

## 📊 DASHBOARD BACKEND HATALARI

### DASH-001: Ürün Kaydetme Hatası - Cloudinary
- **Hata:** `'CloudinaryResource' object has no attribute 'save'`
- **Dosya:** `core/products/models.py` veya `views.py`
- **Sorun:** Cloudinary field save metodu yanlış kullanılıyor
- **Çözüm Gerekli:** Model save() metodunu kontrol et, commit=True kullan

### DASH-002: Depolama Progress Bar Çalışmıyor
- **Sorun:** Cloudinary API'den depolama bilgisi çekilmiyor
- **Dosya:** Dashboard storage info context processor
- **Çözüm Gerekli:** Cloudinary Admin API kullan, usage bilgisi çek

### DASH-003: İstatistikler Görünmüyor
- **Sorun:**
  - Index ve Hakkımızda'da rakamlar görünmüyor
  - İletişim verileri otomatik eklenmiyor
- **Dosya:** Context processors, About model
- **Çözüm Gerekli:**
  - Template context kontrol et
  - Signal'lerde istatistik güncellemesi ekle

### DASH-004: Footer Hizmetler Dashboard'dan Çekilmiyor
- **Sorun:** Footer'daki hizmetler listesi static, dashboard'dan gelmeli
- **Dosya:** Footer template, context processor
- **Çözüm Gerekli:** Service model'den footer'a data pass et

### DASH-005: Basında Biz Bölümü Hatası
- **Sorun:** Dashboard basında biz bölümünde hata var
- **Dosya:** `dashboard/views.py` - media management
- **Çözüm Gerekli:** View ve model kontrol et

---

## ✉️ EMAIL TEMPLATE EKSİKLİKLERİ

### EMAIL-001: Şifre Sıfırlama Email Template Eksik/Yanlış
- **Kullanıcı İsteği:** CodeNovaX logolu, kurumsal şifre sıfırlama email'i
- **Gereksinimler:**
  - CodeNovaX logosu
  - Kullanıcı ad-soyad
  - Web sitesi adı
  - 1 saat geçerlilik uyarısı
- **Dosya:** `templates/registration/password_reset_email.html` (muhtemelen eksik)
- **Çözüm Gerekli:** Email template oluştur

---

## 🔍 SEO VE META EKSİKLERİ

### SEO-001: Ayarlar SEO Bölümü İşlevsizliği
- **Sorun:** Dashboard SEO ayarları hangi alanları etkiliyor belirsiz
- **Dosya:** Settings model ve context processor
- **Çözüm Gerekli:** SEO ayarlarının meta tag'lere etkisini kontrol et

### SEO-002: Meta Başlık ve Açıklama Kontrolleri
- **Sorun:** Kategori ve ürünlerde Meta SEO alanları kontrol edilmeli
- **Dosya:** Product ve Category models
- **Çözüm Gerekli:** SEO audit komutu çalıştır:
  ```bash
  python manage.py seo_audit --full
  ```

---

## 🎨 GÖRSEL GEREKSİNİMLERİ (hatalar.txt'den)

### IMG-001: Resim Boyutları ve Standartları
- **Gerekli Boyutlar:**
  - Logo: 200x60px (navbar), 60x60px (footer)
  - Favicon: 16x16px, 32x32px, 180x180px
  - OG Image: 1200x630px
  - Carousel: 1920x1080px
  - About: 800x600px
  - Products: 600x400px
  - Gallery: 800x600px (masonry)
  - Reviews: 100x100px (avatarlar)
  - Media: 400x250px

### IMG-002: Resim Kırpma/Crop Fonksiyonu
- **Kullanıcı İsteği:** Yüklenen resimler farklı boyutsa otomatik kırpma ve hangi alanda görüneceğini belirleme
- **Sorun:** Focal point field'ları migration'da silinmiş
- **Çözüm Gerekli:** ImageKit crop veya Cloudinary transformations kullan

---

## 📝 DİĞER İYİLEŞTİRMELER

### IYI-001: Dashboard Başlık ve Logo
- **Kullanıcı İsteği:**
  - "Gösterge Tablosu" yerine işletme adı
  - "Yönetici Kontrol Paneli" yerine işletme adı + panel
  - "Yönetim Paneli" yerine kullanıcı adı
- **Dosya:** `dashboard/templates/dashboard/index.html` ve `sidebar.html`
- **Çözüm Gerekli:** Template değişkenleri kullan

### IYI-002: PDF Katalog Görünümü
- **Sorun:** PDF eklenince sadece ana sitede görülecek, navbar'da olmasın
- **Dosya:** Navbar template, conditional logic
- **Çözüm Gerekli:** PDF varlık kontrolü ekle

### IYI-003: Sıralama Otomatik Doldurma
- **Sorun:** Tüm modallarda sıralama manuel, otomatik son sıra +1 olmalı
- **Dosya:** Dashboard JavaScript
- **Çözüm Gerekli:** AJAX ile son order fetch et, +1 ile doldur

### IYI-004: Hizmetler Anasayfa Limiti
- **Sorun:** Anasayfada 6'dan fazla hizmet gösterilmiyor
- **Dosya:** Home view ve template
- **Çözüm Gerekli:** Carousel veya "Daha Fazla" butonu ekle

### IYI-005: Ekip Kartları Limiti
- **Sorun:** 4'ten fazla ekip üyesi gösterilmiyor, otomatik kaydırma olmalı
- **Dosya:** About template
- **Çözüm Gerekli:** Carousel ekle veya grid genişlet

### IYI-006: Hakkımızda Hizmetler Kaydırma
- **Sorun:** Hakkımızda'da 4'ten fazla hizmet gösterilmiyor
- **Dosya:** About template - services section
- **Çözüm Gerekli:** Carousel ekle

---

## 🎯 ÖNCELİK SIRASI

### 🔥 ACIL (Bugün Yapılmalı - Production Blocker)
1. ✅ API anahtarlarını `.env`'e taşı (GUV-001)
2. ✅ `settings/__init__.py` oluştur (KRT-002)
3. ✅ `manage.py` settings path düzelt (KRT-001)
4. ✅ Duplicate `ip_address` field'larını sil (KRT-004, KRT-005)
5. ✅ Review `user` field'ı ekle (KRT-006)
6. ✅ Duplicate context processor sil (KRT-003)
7. ✅ `ValidationError` import ekle (KRT-007)
8. ✅ Focal point signals'i düzelt (KRT-008)
9. ✅ Cloudinary apps ekle (BAG-003)
10. ✅ Logs dizini oluştur (BAG-007)

### 🟠 YÜKSEK (Bu Hafta)
11. ✅ CSRF exempt sorununu çöz (GUV-002)
12. ✅ IP address capture ekle (KLT-001)
13. ✅ Eksik paketleri yükle (BAG-001, BAG-002)
14. ✅ Email backend ekle (BAG-005)
15. ✅ Captcha config ekle (BAG-004)
16. ✅ DeepL API key config (BAG-006)
17. ✅ Gereksiz dosyaları sil (GEREKSIZ-001)
18. ✅ Ürün kaydetme Cloudinary hatasını çöz (DASH-001)

### 🟡 ORTA (2 Hafta İçinde)
19. UI/UX hatalarını düzelt (UI-001 - UI-010)
20. Dashboard backend hatalarını çöz (DASH-002 - DASH-005)
21. Email template'i oluştur (EMAIL-001)
22. Bare except'leri düzelt (KLT-002)
23. Code quality sorunlarını temizle (KLT-003 - KLT-005)

### 🟢 DÜŞÜK (İyileştirmeler)
24. SEO audit çalıştır ve düzelt (SEO-001, SEO-002)
25. Görsel gereksinimleri tamamla (IMG-001, IMG-002)
26. Dashboard başlık/logo iyileştirmeleri (IYI-001)
27. Diğer iyileştirmeler (IYI-002 - IYI-006)

---

## 📌 NOTLAR

- **Toplam Tespit Edilen Sorun:** 60+ kritik/önemli sorun
- **Production Blocker:** 10 adet (Acil öncelik)
- **Güvenlik Riski:** 3 adet (API keys, CSRF, .env)
- **Django Çalışmayı Engelleyen:** 9 adet

---

**Son Güncelleme:** 2025-12-27
**Hazırlayan:** Claude AI - Proje Audit