#core\core\utils.py
import cloudinary.api
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def check_cloudinary_storage():
    """
    Cloudinary depolama kullanımını kontrol eder.
    Returns: dict with usage info
    """
    try:
        # Cloudinary API'den kullanım bilgilerini al
        usage = cloudinary.api.usage()
        
        # Kullanılan alan (bytes cinsinden)
        used_bytes = usage.get('storage', {}).get('usage', 0)
        
        # Paket limiti (settings'den)
        limit_bytes = settings.CLOUDINARY_STORAGE_LIMIT_BYTES
        limit_gb = settings.CLOUDINARY_STORAGE_LIMIT_GB
        
        # Hesaplamalar
        used_gb = used_bytes / (1024 ** 3)
        remaining_bytes = max(0, limit_bytes - used_bytes)
        remaining_gb = remaining_bytes / (1024 ** 3)
        usage_percentage = min(100, (used_bytes / limit_bytes) * 100) if limit_bytes > 0 else 0
        
        # Uyarı seviyeleri
        warning_level = 'success'
        if usage_percentage >= 90:
            warning_level = 'danger'
        elif usage_percentage >= 80:
            warning_level = 'warning'
        elif usage_percentage >= 60:
            warning_level = 'info'
        
        return {
            'used_bytes': used_bytes,
            'used_gb': round(used_gb, 2),
            'limit_bytes': limit_bytes,
            'limit_gb': limit_gb,
            'remaining_bytes': remaining_bytes,
            'remaining_gb': round(remaining_gb, 2),
            'usage_percentage': round(usage_percentage, 1),
            'warning_level': warning_level,
            'is_warning': usage_percentage >= 80,
            'is_critical': usage_percentage >= 90,
        }
        
    except Exception as e:
        logger.error(f"Cloudinary storage check failed: {e}")
        return {
            'used_bytes': 0,
            'used_gb': 0,
            'limit_bytes': settings.CLOUDINARY_STORAGE_LIMIT_BYTES,
            'limit_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
            'remaining_bytes': settings.CLOUDINARY_STORAGE_LIMIT_BYTES,
            'remaining_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
            'usage_percentage': 0,
            'warning_level': 'success',
            'is_warning': False,
            'is_critical': False,
            'error': True
        }

def is_storage_limit_exceeded():
    """Depolama limiti aşıldı mı kontrol eder"""
    usage_info = check_cloudinary_storage()
    if 'error' in usage_info:
        return False
    return usage_info['usage_percentage'] >= 95  # %95 dolduğunda uyarı


def get_storage_package_display():
    """Admin panelinde paket bilgilerini göstermek için"""
    storage_info = check_cloudinary_storage()
    return f"{settings.CLOUDINARY_STORAGE_LIMIT_GB}GB Paket - %{storage_info.get('usage_percentage', 0)} kullanım"