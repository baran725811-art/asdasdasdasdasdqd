# gallery/admin.py
from django.contrib import admin
from django.utils.html import format_html
from core.widgets import GalleryCropWidget
from django import forms
try:
    from . import translation
except ImportError:
    pass

from .models import Gallery
from modeltranslation.admin import TranslationAdmin




class GalleryAdminForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = '__all__'
        widgets = {
            'cropped_image': GalleryCropWidget(),
        }

class GalleryAdmin(TranslationAdmin):
    form = GalleryAdminForm
    list_display = ('title', 'slug', 'media_type', 'media_preview', 'is_featured', 'is_active', 'order', 'created_at')
    list_filter = ('media_type', 'is_featured', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'slug')
    list_editable = ('is_active', 'is_featured', 'order')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'media_preview_large')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'description', 'media_type')
        }),
        ('Medya Dosyaları', {
            'fields': ('image', 'cropped_image', 'video', 'video_url', 'alt_text', 'media_preview_large'),
        }),
        ('Ayarlar', {
            'fields': ('order', 'is_featured', 'is_active')
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
    readonly_fields = ('slug', 'created_at', 'updated_at', 'media_preview_large')

    
    def media_preview(self, obj):
        """Admin listesinde küçük medya önizlemesi"""
        if obj.media_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.build_url(width=50, height=50, crop='thumb', gravity='auto') if hasattr(obj.image, 'build_url') else obj.image.url
            )
        elif obj.media_type == 'video':
            if obj.video:
                return format_html(
                    '<div style="width: 50px; height: 50px; background: #007cba; color: white; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 12px;">VIDEO</div>'
                )
            elif obj.video_url:
                if obj.is_youtube_video():
                    return format_html(
                        '<div style="width: 50px; height: 50px; background: #ff0000; color: white; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 10px;">YT</div>'
                    )
                elif obj.is_vimeo_video():
                    return format_html(
                        '<div style="width: 50px; height: 50px; background: #1ab7ea; color: white; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 10px;">VM</div>'
                    )
        return "—"
    
    media_preview.short_description = "Önizleme"
    
    def media_preview_large(self, obj):
        """Admin detayında büyük medya önizlemesi - orijinal ve kırpılmış"""
        if obj.media_type == 'image' and obj.image:
            html = '<div style="display: flex; gap: 20px; align-items: flex-start;">'

            # Orijinal resim
            original_url = obj.image.url
            if hasattr(obj.image, 'build_url'):
                original_url = obj.image.build_url(width=300, height=200, crop='limit', gravity='auto')

            html += f'''
            <div style="text-align: center;">
                <h4 style="margin: 0 0 8px 0; color: #666;">Orijinal Resim</h4>
                <img src="{original_url}" style="max-width: 300px; max-height: 200px; object-fit: contain; border-radius: 8px; border: 1px solid #ddd;" />
                <p style="font-size: 12px; color: #888; margin: 4px 0 0 0;">Tam boyut, kırpılmamış</p>
            </div>
            '''

            # Kırpılmış resim (eğer focal point varsa)
            if obj.cropped_image:
                cropped_url = obj.cropped_image.url
                if hasattr(obj.cropped_image, 'build_url'):
                    cropped_url = obj.cropped_image.build_url(width=300, height=200, crop='limit', gravity='auto')
                
                html += f'''
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 8px 0; color: #666;">Kırpılmış Resim</h4>
                    <img src="{cropped_url}" style="max-width: 300px; max-height: 200px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;" />
                    <p style="font-size: 12px; color: #888; margin: 4px 0 0 0;">Kartlarda gösterilecek</p>
                </div>
                '''

            html += '</div>'
            return format_html(html)

        # Video içeriği için mevcut kod
        elif obj.media_type == 'video':
            # ... mevcut video kodunuz
            pass
        
        return "Medya bulunamadı"

    media_preview_large.short_description = "Medya Önizleme (Orijinal vs Kırpılmış)"
    
    def get_queryset(self, request):
        """Admin listesi performansını artırmak için select_related kullan"""
        return super().get_queryset(request).select_related()
    
      
    
    



admin.site.register(Gallery, GalleryAdmin)

