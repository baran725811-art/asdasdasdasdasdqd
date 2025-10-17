# core/services.py
import deepl
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class DeepLTranslationService:
    """
    DeepL API kullanarak çeviri işlemlerini yöneten servis
    """
    
    # DeepL dil kodları eşleştirmesi
    DJANGO_TO_DEEPL_LANG_MAP = {
        'tr': 'TR',
        'en': 'EN-US',
        'fr': 'FR', 
        'de': 'DE',
        'ar': 'AR',
        'ru': 'RU'
    }
    
    def __init__(self, api_key):
        """
        Args:
            api_key (str): DeepL API anahtarı
        """
        self.api_key = api_key
        self.translator = deepl.Translator(api_key)
    
    def translate_text(self, text, target_language, source_language='tr'):
        """
        Metni belirtilen dile çevir
        
        Args:
            text (str): Çevrilecek metin
            target_language (str): Hedef dil kodu (Django formatında: en, fr, de, ar, ru)
            source_language (str): Kaynak dil kodu (varsayılan: tr)
            
        Returns:
            str: Çevrilmiş metin veya hata durumunda None
        """
        if not text or not text.strip():
            return text
            
        # Kaynak ve hedef dil aynıysa çeviri yapma
        if source_language == target_language:
            return text
            
        try:
            # Django dil kodlarını DeepL formatına çevir
            source_lang = self.DJANGO_TO_DEEPL_LANG_MAP.get(source_language, 'TR')
            target_lang = self.DJANGO_TO_DEEPL_LANG_MAP.get(target_language)
            
            if not target_lang:
                logger.error(f"Desteklenmeyen hedef dil: {target_language}")
                return None
                
            # HTML etiketlerini temizle (RichTextField için)
            clean_text = strip_tags(text) if '<' in text and '>' in text else text
            
            # DeepL API ile çeviri yap
            result = self.translator.translate_text(
                clean_text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            translated_text = result.text
            
            logger.info(f"Çeviri başarılı: {source_language} -> {target_language}")
            return translated_text
            
        except deepl.DeepLException as e:
            logger.error(f"DeepL API hatası: {e}")
            return None
        except Exception as e:
            logger.error(f"Çeviri sırasında beklenmeyen hata: {e}")
            return None
    
    def get_usage(self):
        """
        API kullanım bilgilerini getir
        
        Returns:
            dict: Kullanım bilgileri
        """
        try:
            usage = self.translator.get_usage()
            return {
                'character_count': usage.character.count,
                'character_limit': usage.character.limit
            }
        except Exception as e:
            logger.error(f"Kullanım bilgisi alınırken hata: {e}")
            return None
    
    def translate_model_fields(self, instance, fields_to_translate, target_languages=None):
        """
        Model instance'ının belirtilen alanlarını çevirir
        
        Args:
            instance: Django model instance
            fields_to_translate (list): Çevrilecek alan adları
            target_languages (list): Hedef diller (varsayılan: settings'ten alınır)
            
        Returns:
            dict: Çeviri sonuçları {lang: {field: translated_text}}
        """
        if target_languages is None:
            target_languages = [lang[0] for lang in settings.LANGUAGES if lang[0] != 'tr']
        
        translations = {}
        total_characters = 0
        
        for lang in target_languages:
            translations[lang] = {}
            
            for field_name in fields_to_translate:
                # Türkçe alan değerini al
                tr_field_value = getattr(instance, f"{field_name}_tr", None) or getattr(instance, field_name, None)
                
                if tr_field_value:
                    # Karakter sayısını hesapla
                    char_count = len(str(tr_field_value))
                    total_characters += char_count
                    
                    # Çeviri yap
                    translated_text = self.translate_text(
                        str(tr_field_value), 
                        target_language=lang
                    )
                    
                    if translated_text:
                        translations[lang][field_name] = translated_text
                    else:
                        logger.warning(f"Çeviri başarısız: {field_name} -> {lang}")
        
        return translations, total_characters


def get_translation_service(user):
    """
    Kullanıcı için çeviri servisini getir
    
    Args:
        user: Django User instance
        
    Returns:
        DeepLTranslationService veya None
    """
    try:
        company = user.company
        if company and company.deepl_api_key:
            return DeepLTranslationService(company.deepl_api_key)
    except:
        pass
    
    return None