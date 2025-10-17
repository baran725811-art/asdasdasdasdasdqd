# dashboard/models.py - Optimize edilmiş versiyon
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_ckeditor_5.fields import CKEditor5Field
from core.cloudinary_fields import OptimizedImageField, SEOImageMixin


from .constants import LANGUAGE_CHOICES, NOTIFICATION_TYPES


class DashboardSettings(models.Model):
    """Dashboard genel ayarları"""
    site_title = models.CharField(_('Site Başlığı'), max_length=200)
    favicon = OptimizedImageField(_('Favicon'), folder='settings', blank=True)
    logo = OptimizedImageField(_('Logo'), folder='settings', blank=True)
    email = models.EmailField(_('E-posta'), blank=True)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    address = models.TextField(_('Adres'), blank=True)
    facebook = models.URLField(_('Facebook'), blank=True)
    twitter = models.URLField(_('Twitter'), blank=True)
    instagram = models.URLField(_('Instagram'), blank=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    youtube = models.URLField(_('YouTube'), blank=True)
    analytics_code = models.TextField(_('Analytics Kodu'), blank=True)
    meta_title = models.CharField(_('Meta Başlık'), max_length=200, blank=True)
    meta_description = models.TextField(_('Meta Açıklama'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Site Ayarı')
        verbose_name_plural = _('Site Ayarları')

    def __str__(self):
        return self.site_title


class Message(models.Model):
    """Dashboard mesajları"""
    STATUS_CHOICES = (
        ('new', _('Yeni')),
        ('read', _('Okundu')),
        ('replied', _('Yanıtlandı')),
        ('spam', _('Spam')),
    )

    name = models.CharField(_('İsim'), max_length=100)
    email = models.EmailField(_('E-posta'))
    subject = models.CharField(_('Konu'), max_length=200)
    message = models.TextField(_('Mesaj'))
    status = models.CharField(_('Durum'), max_length=10, choices=STATUS_CHOICES, default='new')
    note = models.TextField(_('Not'), blank=True)
    created_at = models.DateTimeField(_('Gönderim Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Mesaj')
        verbose_name_plural = _('Mesajlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class MediaMention(SEOImageMixin, models.Model):
    """Basın haberleri - Optimize edilmiş çeviri alanları ile"""
    # Temel alanlar
    title = models.CharField("Başlık", max_length=200)
    source = models.CharField("Kaynak", max_length=100)
    url = models.URLField("URL", blank=True, max_length=2000)
    publish_date = models.DateField(null=True, blank=True, verbose_name="Yayın Tarihi")
    description = models.TextField("Açıklama", blank=True)
    image = OptimizedImageField("Görsel", folder='media_mentions', blank=True)
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True,
                               help_text="Görsel için SEO alt metni")
    is_active = models.BooleanField("Aktif", default=True)
    order = models.IntegerField("Sıralama", default=0)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)
    
    # Çeviri alanları - constants'dan gelen dil kodları ile
    title_en = models.CharField("Başlık (İngilizce)", max_length=200, blank=True)
    source_en = models.CharField("Kaynak (İngilizce)", max_length=100, blank=True)
    description_en = models.TextField("Açıklama (İngilizce)", blank=True)
    
    title_de = models.CharField("Başlık (Almanca)", max_length=200, blank=True)
    source_de = models.CharField("Kaynak (Almanca)", max_length=100, blank=True)
    description_de = models.TextField("Açıklama (Almanca)", blank=True)
    
    title_fr = models.CharField("Başlık (Fransızca)", max_length=200, blank=True)
    source_fr = models.CharField("Kaynak (Fransızca)", max_length=100, blank=True)
    description_fr = models.TextField("Açıklama (Fransızca)", blank=True)
    
    title_es = models.CharField("Başlık (İspanyolca)", max_length=200, blank=True)
    source_es = models.CharField("Kaynak (İspanyolca)", max_length=100, blank=True)
    description_es = models.TextField("Açıklama (İspanyolca)", blank=True)
    
    title_ru = models.CharField("Başlık (Rusça)", max_length=200, blank=True)
    source_ru = models.CharField("Kaynak (Rusça)", max_length=100, blank=True)
    description_ru = models.TextField("Açıklama (Rusça)", blank=True)
    
    title_ar = models.CharField("Başlık (Arapça)", max_length=200, blank=True)
    source_ar = models.CharField("Kaynak (Arapça)", max_length=100, blank=True)
    description_ar = models.TextField("Açıklama (Arapça)", blank=True)

    class Meta:
        verbose_name = "Basın Haberi"
        verbose_name_plural = "Basın Haberleri"
        ordering = ['order', '-publish_date']

    def __str__(self):
        return self.title
    
    def get_translated_title(self, lang_code='tr'):
        """Belirtilen dilde başlığı getir"""
        if lang_code == 'tr':
            return self.title
        return getattr(self, f'title_{lang_code}', self.title) or self.title
    
    def get_translated_description(self, lang_code='tr'):
        """Belirtilen dilde açıklamayı getir"""
        if lang_code == 'tr':
            return self.description
        return getattr(self, f'description_{lang_code}', self.description) or self.description


class CustomerReview(models.Model):
    """Müşteri yorumları"""
    name = models.CharField(_("Müşteri Adı"), max_length=100)
    review = models.TextField(_("Yorum"))
    rating = models.IntegerField(_("Puan"), choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(_("Yorum Tarihi"), auto_now_add=True)
    is_approved = models.BooleanField(_("Onaylı"), default=False)

    class Meta:
        verbose_name = _("Müşteri Yorumu")
        verbose_name_plural = _("Müşteri Yorumları")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}/5"


class Notification(models.Model):
    """Bildirim modeli"""
    NOTIFICATION_TYPES = (
        ('message', 'Mesaj'),
        ('review', 'Yorum'),
        ('product', 'Ürün'),
        ('system', 'Sistem'),
        
        ('user', 'Kullanıcı'),
    )
    
    title = models.CharField(max_length=200, verbose_name='Başlık')
    message = models.TextField(verbose_name='Mesaj')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system', verbose_name='Tip')
    is_read = models.BooleanField(default=False, verbose_name='Okundu mu?')
    redirect_url = models.URLField(blank=True, null=True, verbose_name='Yönlendirme URL')
    
    # İlişkili model bilgileri (opsiyonel)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')
    
    class Meta:
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_notification_type_display()}"
    
    @classmethod
    def create_notification(cls, title, message, notification_type='system', redirect_url=None):
        """Yeni bildirim oluştur"""
        return cls.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            redirect_url=redirect_url
        )

class DashboardTranslationSettings(models.Model):
    """Dashboard çeviri ayarları - Constants kullanarak optimize edilmiş"""
    
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name="Kullanıcı",
        related_name='translation_settings'
    )
    
    dashboard_language = models.CharField(
        "Dashboard Dili",
        max_length=7,
        choices=LANGUAGE_CHOICES,
        default='tr',
        help_text="Dashboard arayüzünün görüntüleneceği dil"
    )
    
    primary_language = models.CharField(
        "Ana Dil",
        max_length=7,
        choices=LANGUAGE_CHOICES,
        default='tr',
        help_text="Site içeriği için ana dil (her zaman dahil olur)"
    )
    
    enabled_languages = models.JSONField(
        "Site İçin Aktif Diller",
        default=list,
        help_text="Bu kullanıcının site içeriği için çeviri yapacağı diller"
    )
    
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Çeviri Ayarları"
        verbose_name_plural = "Dashboard Çeviri Ayarları"
    
    def __str__(self):
        return f"{self.user.username} - Dashboard Çeviri Ayarları"
    
    def get_all_languages(self):
        """Ana dil + seçilen diller - GÜVENLİ VERSİYON"""
        languages = [self.primary_language] if self.primary_language else ['tr']
        
        # enabled_languages'ı güvenli şekilde işle
        if isinstance(self.enabled_languages, list):
            for lang in self.enabled_languages:
                # Boş string, None, whitespace kontrolü
                if lang and isinstance(lang, str) and lang.strip():
                    lang = lang.strip()
                    # Geçerli dil kodu kontrolü (2-3 karakter, sadece harf)
                    if 2 <= len(lang) <= 3 and lang.isalpha():
                        if lang != self.primary_language and lang not in languages:
                            languages.append(lang)
        
        return languages
    
    def get_language_name(self, lang_code):
        """Dil kodunu adına çevir"""
        from .constants import LANGUAGE_NAMES
        return LANGUAGE_NAMES.get(lang_code, lang_code.upper())
    
    def get_enabled_language_names(self):
        """Aktif dillerin adlarını getir"""
        return [self.get_language_name(lang) for lang in self.get_all_languages()]
    
    @property
    def requires_translation(self):
        """Çeviri gerekiyor mu?"""
        return len(self.get_all_languages()) > 1


# Abstract Base Models for Translation Support
class TranslatableModel(models.Model):
    """Çeviri destekli modeller için abstract base class"""
    
    class Meta:
        abstract = True
    
    def get_translated_field(self, field_name, lang_code='tr'):
        """Belirtilen dilde alanı getir"""
        if lang_code == 'tr' or not hasattr(self, f'{field_name}_{lang_code}'):
            return getattr(self, field_name, '')
        
        translated_value = getattr(self, f'{field_name}_{lang_code}', '')
        return translated_value if translated_value else getattr(self, field_name, '')
    
    def has_translation(self, lang_code):
        """Bu dilde çeviri var mı?"""
        if lang_code == 'tr':
            return True
            
        # Model'in çeviri alanlarını kontrol et
        translation_fields = [f for f in self._meta.fields 
                            if f.name.endswith(f'_{lang_code}')]
        
        for field in translation_fields:
            value = getattr(self, field.name, '')
            if value:
                return True
        return False


# Legacy Models (moved from other apps for dashboard use)
class Category(models.Model):
    """Ürün kategorileri"""
    name = models.CharField(max_length=100, verbose_name='Kategori Adı')
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(verbose_name='Açıklama', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(SEOImageMixin, models.Model):
    """Ürünler"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Kategori')
    name = models.CharField(max_length=200, verbose_name='Ürün Adı')
    slug = models.SlugField(max_length=220, unique=True)
    description = CKEditor5Field(_('Açıklama'), blank=True, config_name='default')
    image = OptimizedImageField(verbose_name='Ürün Görseli', folder='products')
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True,
                               help_text="Ürün görseli için SEO alt metni")
    
    # Fiyat ve stok alanları - isteğe bağlı
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Fiyat', 
                               null=True, blank=True, default=None)
    stock = models.IntegerField(verbose_name='Stok Durumu', null=True, blank=True, default=None)
    
    meta_title = models.CharField(max_length=200, verbose_name='Meta Başlık', blank=True)
    meta_description = models.TextField(verbose_name='Meta Açıklama', blank=True)
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    is_active = models.BooleanField(default=True, verbose_name='Satışta')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def get_price_display(self):
        """Fiyat görüntüleme için yardımcı method"""
        if self.price:
            return f"{self.price} ₺"
        return "Fiyat belirtilmemiş"
    
    def get_stock_display(self):
        """Stok görüntüleme için yardımcı method"""
        if self.stock is not None:
            return f"{self.stock} adet"
        return "Stok belirtilmemiş"
    
    @property
    def is_low_stock(self):
        """Stok az mı?"""
        return self.stock is not None and self.stock <= 5
    


