# core/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
import logging

from django.core.cache import cache
from cloudinary.models import CloudinaryField
# Model imports
from about.models import About, Service, TeamMember
from products.models import Category, Product
from home.models import CarouselSlide
from gallery.models import Gallery
from reviews.models import Review
from core.models import SiteSettings

from .services import get_translation_service

logger = logging.getLogger(__name__)

# Çevirilecek modeller ve alanları
TRANSLATABLE_MODELS = {
    About: ['title', 'short_description', 'mission', 'vision', 'story', 'meta_title', 'meta_description'],
    Service: ['title', 'description'],
    TeamMember: ['name', 'position', 'bio'],
    Category: ['name', 'description', 'meta_title', 'meta_description'],
    Product: ['name', 'description', 'meta_title', 'meta_description'],
    CarouselSlide: ['title', 'description', 'button_text'],
    Gallery: ['title', 'description'],
    Review: ['comment'],
    SiteSettings: ['site_name', 'site_tagline', 'seo_title', 'seo_description', 'seo_keywords', 'pdf_catalog_title', 'contact_address']
}

def auto_translate_instance(sender, instance, created, **kwargs):
    """
    Model instance'ı kaydedildiğinde otomatik çeviri yap
    """
    # Sadece yeni kayıtlar veya belirli koşullarda çeviri yap
    if not created and not should_retranslate(instance):
        return
    
    # Çevirilecek alanları al
    fields_to_translate = TRANSLATABLE_MODELS.get(sender)
    if not fields_to_translate:
        return
    
    # SiteSettings için özel işlem (tek kullanıcı yok)
    if sender == SiteSettings:
        translate_site_settings(instance, fields_to_translate)
        return
    
    # Kullanıcı bilgisini al
    user = get_user_from_request() or get_admin_user()
    if not user:
        logger.warning("Çeviri için kullanıcı bulunamadı")
        return
    
    # Çeviri servisini al
    translation_service = get_translation_service(user)
    if not translation_service:
        logger.warning(f"Kullanıcı {user.username} için çeviri servisi bulunamadı")
        return
    
    # Kullanıcının şirketini kontrol et
    try:
        company = user.company
        if not company or not company.is_active:
            return
    except:
        logger.warning(f"Kullanıcı {user.username} için şirket bulunamadı")
        return
    
    # Çeviri yap
    try:
        translations, total_characters = translation_service.translate_model_fields(
            instance, 
            fields_to_translate
        )
        
        # Karakter limitini kontrol et
        if not company.can_translate(total_characters):
            logger.warning(f"Karakter limiti aşıldı: {company.character_usage + total_characters}/{company.character_limit}")
            return
        
        # Çevirileri kaydet
        for lang, field_translations in translations.items():
            for field_name, translated_text in field_translations.items():
                setattr(instance, f"{field_name}_{lang}", translated_text)
        
        # Instance'ı kaydet (signal tekrarını engellemek için update_fields kullan)
        update_fields = []
        for lang in translations.keys():
            for field_name in fields_to_translate:
                update_fields.append(f"{field_name}_{lang}")
        
        if update_fields:
            instance.save(update_fields=update_fields)
            
            # Karakter kullanımını güncelle
            company.add_character_usage(total_characters)
            
            logger.info(f"{sender.__name__} için {total_characters} karakter çevrildi")
    
    except Exception as e:
        logger.error(f"Otomatik çeviri sırasında hata: {e}")

def translate_site_settings(instance, fields_to_translate):
    """
    SiteSettings için özel çeviri işlemi
    """
    # İlk admin kullanıcısını bul
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        return
        
    translation_service = get_translation_service(admin_user)
    if not translation_service:
        return
    
    try:
        translations, total_characters = translation_service.translate_model_fields(
            instance, 
            fields_to_translate
        )
        
        # Çevirileri kaydet
        for lang, field_translations in translations.items():
            for field_name, translated_text in field_translations.items():
                setattr(instance, f"{field_name}_{lang}", translated_text)
        
        # Instance'ı kaydet
        update_fields = []
        for lang in translations.keys():
            for field_name in fields_to_translate:
                update_fields.append(f"{field_name}_{lang}")
        
        if update_fields:
            instance.save(update_fields=update_fields)
            
        logger.info(f"SiteSettings için {total_characters} karakter çevrildi")
        
    except Exception as e:
        logger.error(f"SiteSettings çevirisi sırasında hata: {e}")

def should_retranslate(instance):
    """
    Mevcut kayıt için yeniden çeviri yapılmalı mı kontrol et
    """
    # Bu fonksiyon genişletilebilir - şimdilik basit bir kontrol
    # Örneğin: sadece Türkçe alanlar değiştiyse çeviri yap
    return True

def get_user_from_request():
    """
    Request'ten kullanıcıyı al (middleware ile set edilmişse)
    """
    # Bu fonksiyon özel middleware ile genişletilebilir
    return None

def get_admin_user():
    """
    Varsayılan admin kullanıcısını getir
    """
    return User.objects.filter(is_superuser=True).first()

# Signal bağlantıları
for model_class in TRANSLATABLE_MODELS.keys():
    post_save.connect(
        auto_translate_instance,
        sender=model_class,
        dispatch_uid=f'auto_translate_{model_class.__name__.lower()}'
    )
    

@receiver(post_save)
@receiver(post_delete)
def clear_storage_cache_on_media_change(sender, **kwargs):
    """Medya dosyası değişikliklerinde storage cache'ini temizle"""
    # CloudinaryField içeren modellerde cache'i temizle
    if hasattr(sender, '_meta'):
        for field in sender._meta.fields:
            if isinstance(field, CloudinaryField):
                cache.delete('cloudinary_storage_info')
                break
            
            

# === FOCAL POINT KÍRPMA SİSTEMİ ===
# Dosyanın sonuna ekleyin (import'lardan sonra, mevcut signal'ların sonrasına)

@receiver(post_save, sender=Gallery)
def create_gallery_focal_crop(sender, instance, created, **kwargs):
    """
    Gallery kaydedildiğinde focal point'e göre gerçek kırpma yap
    """
    if instance.image and instance.focal_point_x and instance.focal_point_y:
        try:
            from PIL import Image as PILImage
            import requests
            import tempfile
            import os
            
            # Orijinal resmi indir
            response = requests.get(instance.image.url)
            response.raise_for_status()
            
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            try:
                # PIL ile resmi aç
                with PILImage.open(temp_file_path) as img:
                    # Focal point koordinatları
                    focal_x = instance.focal_point_x / 100.0  # 0.4565
                    focal_y = instance.focal_point_y / 100.0  # 0.7251
                    
                    # Hedef boyutlar
                    target_width, target_height = 400, 300
                    
                    # Focal point'i merkeze alarak kırp
                    img_width, img_height = img.size
                    
                    # Focal point pixel koordinatları
                    focal_px = int(img_width * focal_x)
                    focal_py = int(img_height * focal_y)
                    
                    # Kırpma alanını hesapla (focal point merkez olacak şekilde)
                    crop_width = min(img_width, int(img_height * target_width / target_height))
                    crop_height = min(img_height, int(img_width * target_height / target_width))
                    
                    # Kırpma sınırları
                    left = max(0, focal_px - crop_width // 2)
                    top = max(0, focal_py - crop_height // 2)
                    right = min(img_width, left + crop_width)
                    bottom = min(img_height, top + crop_height)
                    
                    # Sınırları ayarla
                    if right - left < crop_width:
                        left = max(0, right - crop_width)
                    if bottom - top < crop_height:
                        top = max(0, bottom - crop_height)
                    
                    # Kırp ve yeniden boyutlandır
                    cropped = img.crop((left, top, right, bottom))
                    resized = cropped.resize((target_width, target_height), PILImage.Resampling.LANCZOS)
                    
                    # Cloudinary'ye yükle
                    import cloudinary.uploader
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as output_file:
                        resized.save(output_file.name, 'JPEG', quality=85)
                        
                        result = cloudinary.uploader.upload(
                            output_file.name,
                            folder="gallery/cropped",
                            public_id=f"{instance.slug}_cropped_{int(focal_x*100)}_{int(focal_y*100)}"
                        )
                        
                        # Kırpılmış URL'yi kaydet
                        Gallery.objects.filter(id=instance.id).update(
                            cropped_image_url=result['secure_url']
                        )
                        
                        logger.info(f"Gallery {instance.id} için gerçek focal crop oluşturuldu: {result['secure_url']}")
                        
                        os.unlink(output_file.name)
                        
            finally:
                os.unlink(temp_file_path)
                        
        except Exception as e:
            logger.error(f"Gallery {instance.id} gerçek focal crop hatası: {str(e)}")
@receiver(post_save, sender=Product) 
def create_product_focal_crop(sender, instance, created, **kwargs):
    """
    Product kaydedildiğinde focal point'e göre kırpılmış URL oluştur
    """
    if instance.image and instance.focal_point_x and instance.focal_point_y:
        try:
            # Focal point koordinatları normalize et
            norm_x = instance.focal_point_x / 100.0
            norm_y = instance.focal_point_y / 100.0
            
            # Kırpılmış URL'i oluştur (600x400 ürün kart boyutu için)
            base_url = instance.image.url
            if '/upload/' in base_url:
                parts = base_url.split('/upload/')
                if len(parts) == 2:
                    cropped_url = f"{parts[0]}/upload/w_600,h_400,c_fill,g_xy_center,x_{norm_x:.2f},y_{norm_y:.2f},q_auto:good,f_auto/{parts[1]}"
                    logger.info(f"Product {instance.id} için focal crop URL oluşturuldu")
                        
        except Exception as e:
            logger.error(f"Product {instance.id} focal crop hatası: {str(e)}")