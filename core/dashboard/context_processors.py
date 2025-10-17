# dashboard/context_processors.py
from django.db import OperationalError
from core.utils import check_cloudinary_storage
from django.core.cache import cache
from django.conf import settings
import logging

def notification_context(request):
    try:
        from .models import Notification
        unread_count = Notification.objects.filter(is_read=False).count()
        latest_notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]
        
        return {
            'unread_notifications_count': unread_count,
            'latest_notifications': latest_notifications
        }
    except (OperationalError, ImportError):
        # Tablo henüz oluşturulmamışsa boş değerler dön
        return {
            'unread_notifications_count': 0,
            'latest_notifications': []
        }
        
    
    


logger = logging.getLogger(__name__)

def storage_info(request):
    """
    Cloudinary storage bilgilerini sadece dashboard sayfalarına ekler
    """
    if request.path.startswith('/dashboard/'):
        # Cache'den storage bilgilerini al (5 dakika cache)
        storage_data = cache.get('cloudinary_storage_info')
        
        if storage_data is None:
            try:
                storage_data = check_cloudinary_storage()
                cache.set('cloudinary_storage_info', storage_data, 60 * 5)  # 5 dakika cache
            except Exception as e:
                logger.error(f"Storage info error: {e}")
                storage_data = {
                    'used_gb': 0,
                    'limit_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
                    'remaining_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
                    'usage_percentage': 0,
                    'warning_level': 'success',
                    'is_warning': False,
                    'is_critical': False,
                    'error': True
                }
        
        return {
            'cloudinary_storage': storage_data,
            'storage_package_info': {
                'current_package_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
                'available_packages': list(settings.CLOUDINARY_STORAGE_PACKAGES.keys()),
                'is_upgradeable': settings.CLOUDINARY_STORAGE_LIMIT_GB < max(settings.CLOUDINARY_STORAGE_PACKAGES.keys()),
            }
        }
    return {}

