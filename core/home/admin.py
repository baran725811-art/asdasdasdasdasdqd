# home/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.html import format_html

from products.models import Product, Category
from gallery.models import Gallery
from contact.models import Contact
from dashboard.models import CustomerReview, MediaMention
from .models import CarouselSlide
from core.widgets import CarouselCropWidget

# Translation import'unu burada yapalım
try:
    from modeltranslation.admin import TranslationAdmin
    # Translation dosyasını manuel import et
    from . import translation
    USE_TRANSLATION = True
except ImportError:
    USE_TRANSLATION = False

# Koşullu admin class
if USE_TRANSLATION:
    @admin.register(CarouselSlide)
    class CarouselSlideAdmin(TranslationAdmin if USE_TRANSLATION else admin.ModelAdmin):
        list_display = ('thumbnail', 'title', 'order', 'is_active', 'created_at')
        list_editable = ('order', 'is_active')
        list_filter = ('is_active',)
        search_fields = ('title', 'description')
        ordering = ('order',)
        readonly_fields = ('slug', 'created_at', 'updated_at')

        # Küçük resim için özel method
        def thumbnail(self, obj):
            if obj.image:
                return format_html(
                    '<img src="{}" style="width:80px; height:auto; border-radius:6px;" />',
                    obj.image.url
                )
            return "—"
        thumbnail.short_description = "Görsel"
        
        fieldsets = (
            ('Temel Bilgiler', {
                'fields': ('title', 'slug', 'description', 'image', 'alt_text')
            }),
            ('Butonlar', {
                'fields': ('button_text', 'button_url', 'secondary_button_text', 'secondary_button_url')
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
            # Sadece image alanına widget uygula
            if 'image' in form.base_fields:
                form.base_fields['image'].widget = CarouselCropWidget()
            return form

        def save_model(self, request, obj, form, change):
            try:
                obj.clean()
                super().save_model(request, obj, form, change)
            except ValidationError as e:
                messages.error(request, str(e))
else:
    @admin.register(CarouselSlide)
    class CarouselSlideAdmin(admin.ModelAdmin):
        list_display = ('title', 'order', 'is_active', 'created_at')
        list_editable = ('order', 'is_active')
        list_filter = ('is_active',)
        search_fields = ('title', 'description')
        ordering = ('order',)
        readonly_fields = ('slug', 'created_at', 'updated_at')
        
        fieldsets = (
            ('Temel Bilgiler', {
                'fields': ('title', 'slug', 'description',  'cropped_image', 'alt_text')
            }),
            ('Butonlar', {
                'fields': ('button_text', 'button_url', 'secondary_button_text', 'secondary_button_url')
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
            # Sadece cropped_image alanına widget uygula
            if 'cropped_image' in form.base_fields:
                form.base_fields['cropped_image'].widget = CarouselCropWidget()
            return form

        def save_model(self, request, obj, form, change):
            try:
                obj.clean()
                super().save_model(request, obj, form, change)
            except ValidationError as e:
                messages.error(request, str(e))


class CustomAdminSite(AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    def index(self, request, extra_context=None):
        # İstatistikleri topla
        stats = {
            'total_products': Product.objects.count(),
            'total_categories': Category.objects.count(),
            'total_gallery_items': Gallery.objects.count(),
            'unread_messages': Contact.objects.filter(is_read=False).count(),
            'pending_reviews': CustomerReview.objects.filter(approved=False).count(),
            'media_mentions': MediaMention.objects.count(),
        }
        
        # Son eklenen ürünler
        latest_products = Product.objects.order_by('-created_at')[:5]
        
        # Son mesajlar
        latest_contacts = Contact.objects.filter(is_read=False).order_by('-created_at')[:5]
        
        # Kategori bazlı ürün sayıları
        categories_with_counts = Category.objects.annotate(
            product_count=Count('product')
        ).order_by('-product_count')[:5]

        context = {
            **self.each_context(request),
            'title': 'Dashboard',
            'stats': stats,
            'latest_products': latest_products,
            'latest_contacts': latest_contacts,
            'categories_with_counts': categories_with_counts,
        }
        if extra_context:
            context.update(extra_context)
            
        return TemplateResponse(request, 'admin/dashboard.html', context)


# Admin sitesini özelleştir
admin_site = CustomAdminSite(name='custom_admin')

# Modelleri yeni admin sitesine kaydet
admin_site.register(Product)
admin_site.register(Category)
admin_site.register(Gallery)
admin_site.register(Contact)