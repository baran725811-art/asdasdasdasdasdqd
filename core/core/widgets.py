# core/widgets.py
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import json

class ImageCropWidget(forms.ClearableFileInput):
    """
    Modern and professional image cropping widget
    """
    
    def __init__(self, crop_type='default', attrs=None):
        self.crop_type = crop_type
        super().__init__(attrs)
    
    def format_value(self, value):
        """Format the current value"""
        if hasattr(value, 'url'):
            return value.url
        return value
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render crop widget with modal"""
        html = super().render(name, value, attrs, renderer)
        
        # Crop configurations
        crop_configs = {
            'carousel': {'width': 1920, 'height': 1080, 'ratio': 16/9},
            'gallery': {'width': 800, 'height': 600, 'ratio': 4/3},
            'products': {'width': 600, 'height': 400, 'ratio': 3/2},
            'categories': {'width': 400, 'height': 250, 'ratio': 8/5},
            'about': {'width': 800, 'height': 600, 'ratio': 4/3},
            'services': {'width': 400, 'height': 250, 'ratio': 8/5},
            'team': {'width': 300, 'height': 300, 'ratio': 1},
            'reviews': {'width': 100, 'height': 100, 'ratio': 1},
            'media': {'width': 400, 'height': 250, 'ratio': 8/5},
            'default': {'width': 800, 'height': 600, 'ratio': 4/3}
        }
        
        config = crop_configs.get(self.crop_type, crop_configs['default'])
        
        crop_html = f'''
        <div class="image-crop-container" data-field-name="{name}" data-crop-type="{self.crop_type}">
            {html}
            
            <!-- Crop Modal -->
            <div class="crop-modal" id="cropModal_{name}" style="display: none;">
                <div class="crop-modal-content">
                    <div class="crop-header">
                        <h3>{_("Resmi Kırp")} - {self.crop_type.title()}</h3>
                        <button type="button" class="crop-close" onclick="closeCropModal('{name}')" 
                                aria-label="{_("Kapat")}">&times;</button>
                    </div>
                    
                    <div class="crop-body">
                        <div class="crop-info">
                            <p><strong>{_("Hedef Boyut")}:</strong> {config['width']} x {config['height']} piksel</p>
                            <p>{_("Kırpmak istediğiniz alanı seçin. Önizleme bölümünde sonucu görebilirsiniz.")}</p>
                        </div>
                        
                        <div class="crop-preview-container">
                            <div class="crop-original">
                                <h4>{_("Orijinal Resim")}</h4>
                                <div class="crop-original-container">
                                    <img id="cropImage_{name}" alt="{_("Kırpılacak resim")}">
                                </div>
                            </div>
                            
                            <div class="crop-result">
                                <h4>{_("Önizleme")}</h4>
                                <div class="crop-preview" id="cropPreview_{name}">
                                    {_("Kırpma alanını seçin")}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="crop-footer">
                        <button type="button" class="btn-crop-cancel" 
                                onclick="closeCropModal('{name}')">{_("İptal")}</button>
                        <button type="button" class="btn-crop-apply" 
                                onclick="applyCrop('{name}')">{_("Kırpmayı Uygula")}</button>
                    </div>
                </div>
            </div>
            
            <!-- Hidden field to store crop data -->
            <input type="hidden" id="cropData_{name}" name="{name}_crop_data" value="">
        </div>
        
        <script>
            // Crop configuration for {name}
            window.cropConfigs = window.cropConfigs || {{}};
            window.cropConfigs['{name}'] = {json.dumps(config)};
        </script>
        '''
        
        return mark_safe(crop_html)
    
    class Media:
        css = {
            'all': ('admin/css/image-crop.css',)
        }
        js = ('admin/js/image-crop.js',)

# Specific crop widgets for different sections
class CarouselCropWidget(ImageCropWidget):
    """Carousel-specific cropping widget (16:9)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='carousel', attrs=attrs)

class GalleryCropWidget(ImageCropWidget):
    """Gallery-specific cropping widget (4:3)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='gallery', attrs=attrs)

class ProductCropWidget(ImageCropWidget):
    """Product-specific cropping widget (3:2)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='products', attrs=attrs)

class CategoryCropWidget(ImageCropWidget):
    """Category-specific cropping widget (8:5)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='categories', attrs=attrs)

class AboutCropWidget(ImageCropWidget):
    """About section cropping widget (4:3)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='about', attrs=attrs)

class ServiceCropWidget(ImageCropWidget):
    """Service-specific cropping widget (8:5)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='services', attrs=attrs)

class TeamCropWidget(ImageCropWidget):
    """Team member cropping widget (1:1)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='team', attrs=attrs)

class ReviewCropWidget(ImageCropWidget):
    """Review avatar cropping widget (1:1)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='reviews', attrs=attrs)

class MediaCropWidget(ImageCropWidget):
    """Media content cropping widget (8:5)"""
    def __init__(self, attrs=None):
        super().__init__(crop_type='media', attrs=attrs)