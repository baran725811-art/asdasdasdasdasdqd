# core/admin.py
from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
try:
    from . import translation
except ImportError:
    pass
from .models import SiteSettings, Company
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from .models import LegalPage, CookieConsent

class SiteSettingsForm(ModelForm):
    """Site ayarları için özel form"""
    
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'seo_description': Textarea(attrs={'rows': 3, 'cols': 80}),
            'seo_keywords': Textarea(attrs={'rows': 2, 'cols': 80}),
            'contact_address': Textarea(attrs={'rows': 3, 'cols': 80}),
            'google_maps_embed_url': Textarea(attrs={'rows': 4, 'cols': 80}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # SEO başlık uzunluk kontrolü
        seo_title = cleaned_data.get('seo_title')
        if seo_title and len(seo_title) > 60:
            raise ValidationError({
                'seo_title': 'SEO başlığı 60 karakterden uzun olamaz.'
            })
        
        # SEO açıklama uzunluk kontrolü
        seo_description = cleaned_data.get('seo_description')
        if seo_description and len(seo_description) > 160:
            raise ValidationError({
                'seo_description': 'SEO açıklama 160 karakterden uzun olamaz.'
            })
        
        return cleaned_data


class SiteSettingsAdmin(TranslationAdmin):
    form = SiteSettingsForm
    
    # Admin listesi
    list_display = ('site_name', 'seo_title', 'pdf_catalog_enabled', 'updated_at')
    
    # Tek kayıt olacağı için listeleme sayfasını direkt düzenleme sayfasına yönlendir
    def changelist_view(self, request, extra_context=None):
        try:
            obj = SiteSettings.objects.get()
            return self.change_view(request, str(obj.pk), extra_context=extra_context)
        except SiteSettings.DoesNotExist:
            # Kayıt yoksa oluştur
            obj = SiteSettings.objects.create()
            return self.change_view(request, str(obj.pk), extra_context=extra_context)
    
    # Fieldset ile gruplandırma - DİL ALANLARI KALDIRILDI
    fieldsets = (
        ('🏠 Site Temel Bilgileri', {
            'fields': ('site_name', 'site_tagline'),
            'description': 'Site adı ve sloganı ayarları'
        }),
        
        ('🔍 SEO Ayarları', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords'),
            'description': 'Arama motoru optimizasyonu ayarları',
            'classes': ('collapse',)
        }),
        
        ('🎨 Renk Ayarları', {
            'fields': ('primary_color', 'secondary_color', 'navbar_color'),
            'description': 'Site renk şeması ayarları',
            'classes': ('collapse',)
        }),
        
        ('🖼️ Logo ve Görsel Ayarları', {
            'fields': ('site_logo', 'favicon'),
            'description': 'Site logosu ve favicon ayarları',
            'classes': ('collapse',)
        }),
        
        ('📄 PDF Katalog Yönetimi', {
            'fields': ('pdf_catalog_enabled', 'pdf_catalog_title', 'pdf_catalog_file'),
            'description': 'Dashboard ile senkronize PDF katalog ayarları. Dashboard\'dan da yönetilebilir.',
            'classes': ('wide',)  # Collapse kaldırdık, her zaman görünür olsun
        }),
        
        ('📱 Sosyal Medya Linkleri', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'whatsapp_number', 'youtube_url'),
            'description': 'Sosyal medya hesap linkleri',
            'classes': ('collapse',)
        }),
        
        ('📞 İletişim Bilgileri', {
            'fields': ('contact_phone', 'contact_email', 'contact_address'),
            'description': 'İletişim detayları',
            'classes': ('collapse',)
        }),
        
        ('🗺️ Google Maps', {
            'fields': ('google_maps_embed_url',),
            'description': 'Harita entegrasyonu',
            'classes': ('collapse',)
        }),
        
        ('🌍 Çeviri Ayarları', {
            'fields': ('translation_enabled',),
            'description': 'Çeviri sistemi kontrolü - Kapalıysa hiçbir çeviri özelliği görünmez',
            'classes': ('collapse',)
        }),
    )
    
    # Salt okunur alanlar
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Eğer kayıt varsa yeni ekleme izni verme (singleton)
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Site ayarları silinemesin
        return False
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Düzenleme modunda
            readonly.extend(['created_at', 'updated_at'])
        return readonly
    
    # PDF Katalog durumu göster
    def pdf_catalog_status(self, obj):
        if obj.pdf_catalog_enabled and obj.pdf_catalog_file:
            return format_html(
                '<span style="color: green;">✅ Aktif</span><br>'
                '<small>📁 Dosya: <a href="{}" target="_blank">{}</a></small><br>'
                '<small>🔗 <a href="/dashboard/catalog/" target="_blank">Dashboard\'dan Yönet</a></small>',
                obj.pdf_catalog_file.url,
                obj.pdf_catalog_file.name.split('/')[-1]
            )
        elif obj.pdf_catalog_file:
            return format_html(
                '<span style="color: orange;">⏸️ Pasif</span><br>'
                '<small>📁 Dosya mevcut ama aktif değil</small><br>'
                '<small>🔗 <a href="/dashboard/catalog/" target="_blank">Dashboard\'dan Aktif Et</a></small>'
            )
        else:
            return format_html(
                '<span style="color: red;">❌ Yok</span><br>'
                '<small>🔗 <a href="/dashboard/catalog/" target="_blank">Dashboard\'dan Yükle</a></small>'
            )
    pdf_catalog_status.short_description = 'PDF Katalog Durumu'
    
    # List display güncelle
    list_display = ('site_name', 'seo_title', 'pdf_catalog_status', 'updated_at')
    
    # Özel metotlar
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
            
            # PDF katalog işlemleri için özel mesajlar
            if 'pdf_catalog_file' in form.changed_data:
                if obj.pdf_catalog_file:
                    self.message_user(
                        request, 
                        f"✅ PDF Katalog dosyası güncellendi: {obj.pdf_catalog_file.name}. "
                        f"Dashboard'dan görüntüleyebilirsiniz: /dashboard/catalog/",
                        level='SUCCESS'
                    )
                else:
                    self.message_user(
                        request, 
                        "📄 PDF Katalog dosyası kaldırıldı.",
                        level='WARNING'
                    )
            
            if 'pdf_catalog_enabled' in form.changed_data:
                status = "aktif edildi" if obj.pdf_catalog_enabled else "pasif edildi"
                self.message_user(
                    request, 
                    f"🔄 PDF Katalog {status}. Değişiklik navbar'da görünecek.",
                    level='SUCCESS' if obj.pdf_catalog_enabled else 'WARNING'
                )
            
            # Genel başarı mesajı
            if not ('pdf_catalog_file' in form.changed_data or 'pdf_catalog_enabled' in form.changed_data):
                self.message_user(
                    request, 
                    f"Site ayarları başarıyla {'güncellendi' if change else 'oluşturuldu'}.",
                    level='SUCCESS'
                )
                
        except ValidationError as e:
            self.message_user(request, f"Hata: {e.message}", level='ERROR')
    
    # Admin başlığını özelleştir
    def get_model_perms(self, request):
        """Model izinlerini özelleştir"""
        perms = super().get_model_perms(request)
        # Add butonunu gizle çünkü singleton
        perms['add'] = False
        return perms
    
    # Özel CSS ve JS ekle
    class Media:
        css = {
            'all': ('admin/css/custom_sitesettings.css',)
        }
        js = ('admin/js/custom_sitesettings.js',)

# Admin site başlığını özelleştir
admin.site.site_header = "Site Yönetim Paneli"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Hoşgeldiniz"

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'character_usage', 'character_limit', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'user__username')
    readonly_fields = ('character_usage', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('DeepL API Ayarları', {
            'fields': ('deepl_api_key', 'character_limit', 'character_usage')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    

class AdminLoginForm(AuthenticationForm):
    captcha = CaptchaField(
        label=_("Güvenlik Kodu"),
        help_text=_("Yukarıdaki kodu girin")
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'vTextField required'})
        self.fields['password'].widget.attrs.update({'class': 'vPasswordField required'})
        self.fields['captcha'].widget.attrs.update({'class': 'vTextField required'})

# Admin site CAPTCHA ayarı
admin.site.login_form = AdminLoginForm
admin.site.login_template = 'admin/login.html'

admin.site.register(SiteSettings, SiteSettingsAdmin)



@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type', 'is_active', 'last_updated')
    list_filter = ('page_type', 'is_active', 'last_updated')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('page_type', 'title', 'slug', 'content', 'is_active')
        }),
        ('SEO Ayarları', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        })
    )

@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ('session_key_short', 'ip_address', 'consent_summary', 'consent_date')
    list_filter = ('necessary_cookies', 'functional_cookies', 'analytics_cookies', 'marketing_cookies', 'consent_date')
    search_fields = ('session_key', 'ip_address')
    readonly_fields = ('session_key', 'consent_date', 'last_updated')
    
    def session_key_short(self, obj):
        return f"{obj.session_key[:10]}..."
    session_key_short.short_description = "Session"
    
    def consent_summary(self, obj):
        types = []
        if obj.necessary_cookies: types.append("Zorunlu")
        if obj.functional_cookies: types.append("Fonksiyonel")
        if obj.analytics_cookies: types.append("Analitik")
        if obj.marketing_cookies: types.append("Pazarlama")
        return ", ".join(types)
    consent_summary.short_description = "Kabul Edilen Türler"