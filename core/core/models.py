# core/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
class SiteSettings(models.Model):
    """
    Site geneli ayarlar - Singleton pattern kullanarak tek kayıt tutacağız
    """
    # Site Temel Bilgileri
    site_name = models.CharField(
        "Site Adı", 
        max_length=100, 
        default="Baran Anahtarcı",
        help_text="Site başlığında ve SEO'da kullanılacak ana isim"
    )
    site_tagline = models.CharField(
        "Site Sloganı", 
        max_length=200, 
        default="Profesyonel Anahtarcılık Hizmetleri",
        help_text="Site adının yanında görünecek slogan"
    )
    
    # SEO Ayarları
    seo_title = models.CharField(
        "SEO Başlık", 
        max_length=60, 
        default="Baran Anahtarcı - Profesyonel Anahtarcılık Hizmetleri",
        help_text="Tarayıcı başlığında ve Google'da görünecek başlık (max 60 karakter)"
    )
    seo_description = models.TextField(
        "SEO Açıklama", 
        max_length=160, 
        default="Baran Anahtarcı 7/24 çilingir hizmeti sunar. Uygun fiyat, hızlı hizmet.",
        help_text="Google arama sonuçlarında görünecek açıklama (max 160 karakter)"
    )
    seo_keywords = models.TextField(
        "SEO Anahtar Kelimeler", 
        default="anahtarcı, çilingir, kilit, güvenlik sistemleri, Baran Anahtarcı",
        help_text="Virgül ile ayrılmış anahtar kelimeler"
    )
    
    # Site Renk Ayarları
    primary_color = models.CharField(
        "Ana Renk",
        max_length=7,
        default="#1a1a2e",
        validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$', message="Geçerli bir hex renk kodu girin (örn: #1a1a2e)")],
        help_text="Site ana rengi (hex formatında)"
    )
    secondary_color = models.CharField(
        "İkincil Renk",
        max_length=7,
        default="#e94560",
        validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$', message="Geçerli bir hex renk kodu girin (örn: #e94560)")],
        help_text="Butonlar ve vurgular için kullanılacak renk"
    )
    navbar_color = models.CharField(
        "Navbar Rengi",
        max_length=7,
        default="#1a1a2e",
        validators=[RegexValidator(regex=r'^#[0-9A-Fa-f]{6}$', message="Geçerli bir hex renk kodu girin")],
        help_text="Üst menü bar rengi"
    )
    
    # Logo ve Görsel Ayarları
    site_logo = models.ImageField(
        "Site Logosu",
        upload_to='site/',
        blank=True,
        null=True,
        help_text="Navbar'da görünecek logo (önerilen boyut: 120x40px)"
    )
    favicon = models.ImageField(
        "Favicon",
        upload_to='site/',
        blank=True,
        null=True,
        help_text="Tarayıcı sekmesinde görünecek küçük ikon (32x32px)"
    )
    
    # PDF Katalog Ayarları
    pdf_catalog_enabled = models.BooleanField(
        "PDF Katalog Aktif",
        default=False,
        help_text="Aktif edilirse navbar'da 'Katalog' linki görünür"
    )
    pdf_catalog_file = models.FileField(
        "PDF Katalog Dosyası",
        upload_to='catalogs/',
        blank=True,
        null=True,
        help_text="İndirilebilir PDF katalog dosyası"
    )
    pdf_catalog_title = models.CharField(
        "PDF Katalog Başlığı",
        max_length=100,
        default="Ürün Kataloğu",
        help_text="Katalog linkinde görünecek metin"
    )
    
    # Sosyal Medya Linkleri
    facebook_url = models.URLField("Facebook URL", blank=True, null=True)
    instagram_url = models.URLField("Instagram URL", blank=True, null=True)
    twitter_url = models.URLField("Twitter (X) URL", blank=True, null=True)
    whatsapp_number = models.CharField(
        "WhatsApp Numarası",
        max_length=20,
        blank=True,
        null=True,
        help_text="Ülke kodu ile birlikte (örn: +905551234567)"
    )
    youtube_url = models.URLField("YouTube URL", blank=True, null=True)
    
    # İletişim Bilgileri
    contact_phone = models.CharField(
        "Telefon Numarası",
        max_length=20,
        default="+90 xxx xxx xx xx",
        help_text="Görüntülenecek telefon numarası"
    )
    contact_email = models.EmailField(
        "E-posta Adresi",
        default="info@barananahtarci.com",
        help_text="İletişim e-posta adresi"
    )
    contact_address = models.TextField(
        "Adres",
        default="Adres bilgisi",
        help_text="Fiziksel adres bilgisi"
    )
    
    # Google Maps
    google_maps_embed_url = models.TextField(
        "Google Maps Embed URL",
        blank=True,
        null=True,
        help_text="Google Maps'ten alınan embed iframe URL'si"
    )
    
    # Sistem Alanları
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)
    
    class Meta:
        verbose_name = "Site Ayarları"
        verbose_name_plural = "Site Ayarları"
    
    def __str__(self):
        return f"{self.site_name} - Site Ayarları"
    
    def save(self, *args, **kwargs):
        # Singleton pattern - sadece bir kayıt olmasını sağla
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError('Site ayarları zaten mevcut. Mevcut kaydı düzenleyiniz.')
        
        result = super().save(*args, **kwargs)
        
        # Site ayarları değiştiğinde cache'i temizle
        from django.core.cache import cache
        cache.delete('site_settings')
        
        return result
    
    def clean(self):
        # PDF katalog kontrolleri
        if self.pdf_catalog_enabled and not self.pdf_catalog_file:
            raise ValidationError('PDF katalog aktif ise dosya yüklenmeli.')
        
        # WhatsApp numarası formatı kontrolü
        if self.whatsapp_number:
            if not self.whatsapp_number.startswith('+'):
                raise ValidationError('WhatsApp numarası + ile başlamalı (örn: +905551234567)')
    
    @classmethod
    def get_current(cls):
        """Mevcut site ayarlarını getir, yoksa varsayılan değerlerle oluştur"""
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls.objects.create()
    
    def get_whatsapp_link(self):
        """WhatsApp mesaj linki oluştur"""
        if self.whatsapp_number:
            clean_number = self.whatsapp_number.replace('+', '').replace(' ', '')
            return f"https://wa.me/{clean_number}"
        return None
    
    
    
    
    
    # Mevcut SiteSettings modeline bu alanları EKLE:
    translation_enabled = models.BooleanField(
        "Çeviri Sistemi Aktif",
        default=False,
        help_text="Bu ayar kapalıysa çeviri ile ilgili hiçbir alan görünmez"
    )
    
    
class Company(models.Model):
    """
    Müşteri şirketleri - Her kullanıcı bir şirkete bağlı
    """
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı",
        related_name='company'
    )
    name = models.CharField("Şirket Adı", max_length=200)
    deepl_api_key = models.CharField(
        "DeepL API Anahtarı", 
        max_length=100,
        help_text="Bu şirket için özel DeepL API anahtarı"
    )
    character_usage = models.PositiveIntegerField(
        "Kullanılan Karakter Sayısı", 
        default=0,
        help_text="Bu ay kullanılan toplam karakter sayısı"
    )
    character_limit = models.PositiveIntegerField(
        "Karakter Limiti", 
        default=500000,
        help_text="Aylık karakter kullanım limiti"
    )
    is_active = models.BooleanField("Aktif", default=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    class Meta:
        verbose_name = "Şirket"
        verbose_name_plural = "Şirketler"

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def can_translate(self, character_count):
        """Çeviri yapılabilir mi kontrol et"""
        return (self.character_usage + character_count) <= self.character_limit
    
    def add_character_usage(self, character_count):
        """Karakter kullanımını artır"""
        self.character_usage += character_count
        self.save(update_fields=['character_usage'])
        






class LegalPage(models.Model):
    LEGAL_PAGE_TYPES = [
        ('privacy', 'Gizlilik Politikası'),
        ('terms', 'Kullanım Şartları'),
        ('cookies', 'Çerez Politikası'),
    ]
    
    page_type = models.CharField(
        "Sayfa Türü",
        max_length=20,
        choices=LEGAL_PAGE_TYPES,
        unique=True,
        help_text="Yasal sayfa türünü seçin"
    )
    
    title = models.CharField("Başlık", max_length=200)
    slug = models.SlugField("SEO URL", max_length=250, unique=True, blank=True)
    
    content = CKEditor5Field(
        "İçerik", 
        config_name='default',
        help_text="Yasal sayfa içeriğini buraya girin"
    )
    
    # SEO Meta Fields
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    is_active = models.BooleanField("Aktif", default=True)
    last_updated = models.DateTimeField("Son Güncelleme", auto_now=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)

    class Meta:
        verbose_name = "Yasal Sayfa"
        verbose_name_plural = "Yasal Sayfalar"
        ordering = ['page_type']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        # Varsayılan başlık ve meta bilgileri
        if not self.title:
            self.title = dict(self.LEGAL_PAGE_TYPES)[self.page_type]
            
        if not self.meta_title:
            self.meta_title = self.title
            
        if not self.meta_description:
            descriptions = {
                'privacy': 'Kişisel verilerinizin nasıl toplandığı, kullanıldığı ve korunduğu hakkında bilgi.',
                'terms': 'Web sitemizi kullanırken uymanız gereken kurallar ve şartlar.',
                'cookies': 'Web sitemizde kullanılan çerezler ve tercihlerinizi nasıl yöneteceğiniz.'
            }
            self.meta_description = descriptions.get(self.page_type, '')
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('legal_page_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

# Çerez tercihlerini veritabanında saklamak için model (opsiyonel)
class CookieConsent(models.Model):
    session_key = models.CharField("Oturum Anahtarı", max_length=40, unique=True)
    ip_address = models.GenericIPAddressField("IP Adresi", null=True, blank=True)
    
    # Çerez kategorileri
    necessary_cookies = models.BooleanField("Zorunlu Çerezler", default=True)
    functional_cookies = models.BooleanField("Fonksiyonel Çerezler", default=False)
    analytics_cookies = models.BooleanField("Analitik Çerezler", default=False)
    marketing_cookies = models.BooleanField("Pazarlama Çerezleri", default=False)
    
    consent_date = models.DateTimeField("Onay Tarihi", auto_now_add=True)
    last_updated = models.DateTimeField("Son Güncelleme", auto_now=True)

    class Meta:
        verbose_name = "Çerez Onayı"
        verbose_name_plural = "Çerez Onayları"
        ordering = ['-consent_date']

    def __str__(self):
        return f"Çerez Onayı - {self.session_key[:10]}... ({self.consent_date})"