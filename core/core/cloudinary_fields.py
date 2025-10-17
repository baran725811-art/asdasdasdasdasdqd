#core\core\cloudinary_fields.py
from cloudinary.models import CloudinaryField, CloudinaryResource
from cloudinary import CloudinaryImage
from django.core.exceptions import ValidationError
from django.conf import settings

# Bölümlere göre optimal boyutlar
IMAGE_TRANSFORMATIONS = {
    'carousel': {
        'width': 1920,
        'height': 1080,
        'crop': 'fill',
        'gravity': 'auto',
        'quality': 'auto:best',
        'fetch_format': 'auto'
    },
    'gallery': {
        'width': 800,
        'height': 600,
        'crop': 'fill',
        'gravity': 'auto',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'products': {
        'width': 600,
        'height': 400,
        'crop': 'fill',
        'gravity': 'auto',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'categories': {
        'width': 400,
        'height': 250,
        'crop': 'fill',
        'gravity': 'auto',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'about': {
        'width': 800,
        'height': 600,
        'crop': 'fill',
        'gravity': 'auto',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'services': {
        'width': 400,
        'height': 250,
        'crop': 'fill',
        'gravity': 'auto',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'team': {
        'width': 300,
        'height': 300,
        'crop': 'fill',
        'gravity': 'face',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'reviews': {
        'width': 100,
        'height': 100,
        'crop': 'thumb',
        'gravity': 'face',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'media': {
        'width': 400,
        'height': 250,
        'crop': 'fill',
        'gravity': 'auto',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    },
    'site': {
        'width': 200,
        'height': 60,
        'crop': 'fit',
        'gravity': 'center',
        'quality': 'auto:good',
        'fetch_format': 'auto'
    }
}

# CloudinaryResource'a get_transformed_url metodunu ekle
def get_transformed_url_method(self, **transformation_params):
    """Manuel transformasyon için method"""
    if not self or not str(self):
        return ''
    
    try:
        # CloudinaryImage instance oluştur
        cloudinary_image = CloudinaryImage(str(self))
        
        # Default parametreler
        default_params = {
            'quality': 'auto:good',
            'fetch_format': 'auto'
        }
        
        # Parametreleri birleştir
        final_params = {**default_params, **transformation_params}
        
        # URL oluştur
        return cloudinary_image.build_url(**final_params)
        
    except Exception as e:
        # Hata durumunda normal URL döndür
        return self.url if hasattr(self, 'url') else ''

# CloudinaryResource'a method ekle
CloudinaryResource.get_transformed_url = get_transformed_url_method

class OptimizedImageField(CloudinaryField):
    """Bölüme göre otomatik boyutlandırma yapan Cloudinary field"""
    
    def __init__(self, *args, **kwargs):
        # folder parametresinden boyut tipini al
        folder = kwargs.get('folder', 'default')
        
        # Django'nun upload_to parametresini kaldır
        kwargs.pop('upload_to', None)
        
        # Folder'a göre transformasyon seç
        transformation = self._get_transformation_for_folder(folder)
        kwargs.setdefault('transformation', transformation)
        kwargs.setdefault('resource_type', 'image')
        
        super().__init__(*args, **kwargs)
    
    def _get_transformation_for_folder(self, folder):
        """Folder'a göre uygun transformasyonu döndür"""
        # Alt folder'ları da kontrol et
        for key, transform in IMAGE_TRANSFORMATIONS.items():
            if key in folder.lower():
                return transform
        
        # Varsayılan transformasyon
        return {
            'width': 800,
            'height': 600,
            'crop': 'fill',
            'gravity': 'auto',
            'quality': 'auto:good',
            'fetch_format': 'auto'
        }

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value and hasattr(value, 'bytes'):
            # Dosya boyutu kontrolü (20MB limit)
            max_size = getattr(settings, 'CLOUDINARY_MAX_IMAGE_SIZE', 20 * 1024 * 1024)
            if value.bytes > max_size:
                raise ValidationError(f'Resim dosyası çok büyük. Maksimum {max_size // (1024*1024)}MB olmalı.')

class OptimizedVideoField(CloudinaryField):
    """Video için optimize edilmiş field"""
    
    def __init__(self, *args, **kwargs):
        kwargs.pop('upload_to', None)
        
        # Video transformasyonları
        kwargs.setdefault('transformation', {
            'quality': 'auto',
            'fetch_format': 'auto',
            'width': 1280,
            'height': 720,
            'crop': 'limit'
        })
        kwargs.setdefault('resource_type', 'video')
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value and hasattr(value, 'bytes'):
            # Video dosya boyutu kontrolü (100MB limit)
            max_size = getattr(settings, 'CLOUDINARY_MAX_VIDEO_SIZE', 100 * 1024 * 1024)
            if value.bytes > max_size:
                raise ValidationError(f'Video dosyası çok büyük. Maksimum {max_size // (1024*1024)}MB olmalı.')

# SEO Alt Text Mixin
class SEOImageMixin:
    """SEO alt text için mixin"""
    
    def get_alt_text(self):
        """Alt text yoksa title veya name alanını döndür"""
        alt_text = getattr(self, 'alt_text', '')
        if alt_text:
            return alt_text
        
        # Fallback olarak title veya name alanını kullan
        title = getattr(self, 'title', '') or getattr(self, 'name', '')
        return title[:125] if title else 'Resim'
    
    def clean(self):
        super().clean() if hasattr(super(), 'clean') else None
        
        # Alt text yoksa otomatik oluştur
        if hasattr(self, 'alt_text') and not self.alt_text:
            title = getattr(self, 'title', '') or getattr(self, 'name', '')
            if title:
                self.alt_text = title[:125]

# Template için yardımcı fonksiyonlar
def get_optimized_image_url(image_field, width=None, height=None, crop='fill', **kwargs):
    """Template'de kullanım için optimize edilmiş URL döndür"""
    if not image_field:
        return None
    
    if hasattr(image_field, 'get_transformed_url'):
        return image_field.get_transformed_url(width=width, height=height, crop=crop, **kwargs)
    
    # Fallback
    return image_field.url if image_field else None



class RawImageField(CloudinaryField):
    """Orijinal resmi saklayan field (transformasyon uygulanmaz)"""
    
    def __init__(self, *args, **kwargs):
        # Django'nun upload_to parametresini kaldır
        kwargs.pop('upload_to', None)
        
        # Sadece temel kalite ayarları, boyut değişikliği YOK
        kwargs.setdefault('transformation', {
            'quality': 'auto:good',
            'fetch_format': 'auto'
            # crop, width, height YOK - tam orijinal
        })
        kwargs.setdefault('resource_type', 'image')
        
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value and hasattr(value, 'bytes'):
            # Dosya boyutu kontrolü (20MB limit)
            max_size = getattr(settings, 'CLOUDINARY_MAX_IMAGE_SIZE', 20 * 1024 * 1024)
            if value.bytes > max_size:
                raise ValidationError(f'Resim dosyası çok büyük. Maksimum {max_size // (1024*1024)}MB olmalı.')