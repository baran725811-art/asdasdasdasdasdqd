# products/admin.py 
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget
from core.widgets import ProductCropWidget

try:
    from . import translation
except ImportError:
    pass

from .models import Category, Product
from modeltranslation.admin import TranslationAdmin


class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditor5Widget(config_name='default'), required=False)
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'cropped_image': ProductCropWidget(),
        }

class CategoryAdmin(TranslationAdmin):
    list_display = ['name', 'slug', 'product_count', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'slug']
    list_editable = ['order', 'is_active']
    readonly_fields = ('slug', 'created_at', 'updated_at', 'image_preview')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'image', 'alt_text', 'image_preview')
        }),
        ('Ayarlar', {
            'fields': ('order', 'is_active')
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
    
    def product_count(self, obj):
        """Kategorideki aktif ürün sayısını göster"""
        count = obj.get_product_count()
        return f"{count} ürün"
    
    product_count.short_description = "Ürün Sayısı"
    
    def image_preview(self, obj):
        """Ürün kırpılmış görsel önizlemesi"""
        if obj.cropped_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px; '
                'object-fit: cover; border-radius: 8px;" />',
                obj.cropped_image.url
            )
        return "Görsel yok"

    image_preview.short_description = "Kırpılmış Görsel Önizleme"


class ProductAdmin(TranslationAdmin):
    form = ProductAdminForm
    list_display = ['name', 'slug', 'category', 'price_display', 'discount_display', 
                   'stock_display', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at', 'brand']
    search_fields = ['name', 'description', 'slug', 'sku']
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ('slug', 'created_at', 'updated_at', 'image_preview')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'category', 'short_description', 'description')
        }),
        ('Görsel', {
            'fields': ('image', 'cropped_image', 'alt_text', 'image_preview'),
            'description': 'Orijinal Resim: Tam boyut resim (kırpılmaz) | Kırpılmış Resim: Kartlarda gösterilecek'
        }),
        ('Fiyat ve Stok', {
            'fields': ('price', 'discount_price', 'stock', 'sku')
        }),
        ('Ek Bilgiler', {
            'fields': ('brand', 'weight'),
            'classes': ('collapse',)
        }),
        ('Ayarlar', {
            'fields': ('is_active', 'is_featured')
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
    
    def price_display(self, obj):
        """Fiyat görüntüleme"""
        if obj.price:
            if obj.has_discount():
                return format_html(
                    '<span style="text-decoration: line-through; color: #999;">{} ₺</span><br>'
                    '<strong style="color: #d32f2f;">{} ₺</strong>',
                    obj.price, obj.discount_price
                )
            return f"{obj.price} ₺"
        return "—"
    
    price_display.short_description = "Fiyat"
    
    def discount_display(self, obj):
        """İndirim yüzdesi görüntüleme"""
        if obj.has_discount():
            return format_html(
                '<span style="background: #d32f2f; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">%{}</span>',
                obj.get_discount_percentage()
            )
        return "—"
    
    discount_display.short_description = "İndirim"
    
    def stock_display(self, obj):
        """Stok durumu görüntüleme"""
        if obj.stock is not None:
            if obj.stock > 10:
                color = "#4caf50"  # Yeşil
            elif obj.stock > 0:
                color = "#ff9800"  # Turuncu
            else:
                color = "#f44336"  # Kırmızı
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} adet</span>',
                color, obj.stock
            )
        return "Belirtilmemiş"
    
    stock_display.short_description = "Stok"
    
    def image_preview(self, obj):
        """Ürün görseli önizlemesi"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "Görsel yok"
    
    image_preview.short_description = "Görsel Önizleme"
    
    def get_queryset(self, request):
        """Admin listesi performansını artırmak için select_related kullan"""
        return super().get_queryset(request).select_related('category')

    def save_model(self, request, obj, form, change):
        """SKU otomatik oluşturma (eğer boşsa)"""
        if not obj.sku and not change:
            # Basit SKU oluşturma: kategori kısaltması + ID
            category_code = obj.category.name[:3].upper()
            obj.save()  # Önce kaydet ki ID oluşsun
            obj.sku = f"{category_code}-{obj.pk:04d}"
        
        super().save_model(request, obj, form, change)
        


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

