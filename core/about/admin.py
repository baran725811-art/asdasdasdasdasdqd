# about/admin.py 
from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from core.widgets import AboutCropWidget, ServiceCropWidget, TeamCropWidget
from .models import Service




# Translation modülünü import et
try:
    from . import translation
except ImportError:
    pass

from .models import About, Service, TeamMember
from modeltranslation.admin import TranslationAdmin







# About için özel form - CKEditor widget'ları ekle
class AboutAdminForm(forms.ModelForm):
    mission = forms.CharField(widget=CKEditor5Widget(config_name='default'), required=False)
    vision = forms.CharField(widget=CKEditor5Widget(config_name='default'), required=False)
    story = forms.CharField(widget=CKEditor5Widget(config_name='default'), required=False)
    
    class Meta:
        model = About
        fields = '__all__'

class AboutAdmin(TranslationAdmin):
    form = AboutAdminForm
    list_display = ('title', 'slug', 'updated_at')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    prepopulated_fields = {}
    
    fieldsets = (   
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'short_description',  'cropped_image', 'alt_text')
        }),

        ('İçerik', {
            'fields': ('mission', 'vision', 'story')
        }),
        ('İstatistikler', {
            'fields': ('years_experience', 'completed_jobs', 'happy_customers', 
                      'total_services', 'customer_satisfaction'),
            'classes': ('collapse',)
        }),
        ('SEO Ayarları', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
            'description': 'Arama motoru optimizasyonu için meta bilgileri'
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Her dil için cropped_image widget'ını ata
        for field_name in form.base_fields:
            if field_name.startswith('cropped_image'):
                form.base_fields[field_name].widget = AboutCropWidget()
        return form

    def has_add_permission(self, request):
        try:
            if About.objects.exists():
                return False
            return True
        except:
            return True

    def has_delete_permission(self, request, obj=None):
        return False

# Service Admin - GÜNCELLENMIŞ VERSİYON (kırpma widget'ı eklendi)
class ServiceAdmin(TranslationAdmin):
    list_display = ['title', 'slug', 'is_active', 'is_footer', 'order', 'created_at']
    list_filter = ['is_active', 'is_footer', 'created_at']
    search_fields = ['title', 'description', 'slug']
    ordering = ['-is_footer', 'order']
    list_editable = ['order', 'is_active', 'is_footer']
    readonly_fields = ('slug', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'description',  'cropped_image', 'alt_text')
        }),
        ('Görünüm Ayarları', {
            'fields': ('is_active', 'is_footer', 'order'),
            'description': 'is_footer: Footer\'da gösterilecek hizmetleri seçin (maksimum 6 adet)'
        }),
        ('SEO Ayarları', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Her dil için image widget'ını ata
        for field_name in form.base_fields:
            if field_name.startswith('image') and not field_name.startswith('cropped'):
                form.base_fields[field_name].widget = ServiceCropWidget()
        return form
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-is_footer', 'order')

class TeamMemberAdmin(TranslationAdmin):
    list_display = ['name', 'slug', 'position', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'position']
    search_fields = ['name', 'position', 'bio', 'slug']
    ordering = ['order']
    list_editable = ['order', 'is_active']
    readonly_fields = ('slug', 'created_at', 'updated_at')
    
    fieldsets = (
         ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'position', 'bio',  'cropped_image', 'alt_text')
        }),
        ('Ayarlar', {
            'fields': ('order', 'is_active')
        }),
        ('SEO Ayarları', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Her dil için image widget'ını ata
        for field_name in form.base_fields:
            if field_name.startswith('image') and not field_name.startswith('cropped'):
                form.base_fields[field_name].widget = TeamCropWidget()
        return form

# Modelleri kaydet
admin.site.register(About, AboutAdmin)
admin.site.register(Service, ServiceAdmin) 
admin.site.register(TeamMember, TeamMemberAdmin)