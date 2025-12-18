# dashboard/widgets.py - YENİ DOSYA OLUŞTUR

from core.widgets import ImageCropWidget

class DashboardImageCropWidget(ImageCropWidget):
    """Dashboard için özelleştirilmiş kırpma widget'ı"""
    
    class Meta:
        css = {
            'all': ('dashboard/css/components/image-crop.css',)
        }
        js = ('dashboard/js/components/image-crop.js',)