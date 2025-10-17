# dashboard/translation_utils.py
"""
Çeviri işlemleri için ortak yardımcı fonksiyonlar
"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from .constants import LANGUAGE_NAMES, SUPPORTED_LANGUAGES


class TranslationManager:
    """Çeviri işlemlerini yöneten merkezi sınıf"""
    
    @staticmethod
    def get_user_translation_settings(user):
        """Kullanıcının çeviri ayarlarını al"""
        from core.models import SiteSettings
        from .models import DashboardTranslationSettings
        
        site_settings = SiteSettings.get_current()
        translation_enabled = site_settings.translation_enabled
        
        enabled_languages = ['tr']  # Varsayılan
        user_translation_settings = None
        
        if translation_enabled and user.is_authenticated:
            user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
                user=user,
                defaults={'enabled_languages': ['tr']}
            )
            enabled_languages = user_translation_settings.get_all_languages()
        
        return {
            'translation_enabled': translation_enabled,
            'enabled_languages': enabled_languages,
            'user_translation_settings': user_translation_settings,
        }
    
    @staticmethod
    def handle_translation_form_errors(form, enabled_languages, request):
        """Çeviri form hatalarını işle ve mesajları göster"""
        translation_errors = []
        regular_errors = []
        
        for field, errors in form.errors.items():
            if TranslationManager._is_translation_field(field):
                for error in errors:
                    lang_code = field.split('_')[-1]
                    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                    field_name = field.replace(f'_{lang_code}', '')
                    translation_errors.append(f'{field_name}: {error}')
                    messages.error(request, f'{field_name.title()} {lang_name} çevirisi zorunludur.')
            else:
                for error in errors:
                    regular_errors.append(f'{field}: {error}')
                    messages.error(request, f'{field}: {error}')
        
        # Eğer sadece çeviri hataları varsa özel mesaj göster
        if translation_errors and not regular_errors:
            messages.warning(request, f'Seçtiğiniz {len(enabled_languages)-1} dil için çeviri alanlarını doldurmanız zorunludur.')
        
        return {
            'translation_errors': translation_errors,
            'regular_errors': regular_errors,
            'has_translation_errors': bool(translation_errors),
            'has_regular_errors': bool(regular_errors),
        }
    
    @staticmethod
    def _is_translation_field(field_name):
        """Alanın çeviri alanı olup olmadığını kontrol et"""
        return any(f'_{lang}' in field_name for lang in SUPPORTED_LANGUAGES)
    
    @staticmethod
    def get_language_name(lang_code):
        """Dil kodunu adına çevir"""
        return LANGUAGE_NAMES.get(lang_code, lang_code.upper())
    
    @staticmethod
    def validate_translation_fields(cleaned_data, model_name, enabled_languages):
        """Çeviri alanlarını validate et"""
        from .constants import TRANSLATION_REQUIRED_FIELDS
        
        if len(enabled_languages) <= 1:
            return cleaned_data
            
        required_fields = TRANSLATION_REQUIRED_FIELDS.get(model_name, [])
        validation_errors = {}
        
        for lang_code in enabled_languages:
            if lang_code != 'tr':  # Ana dil hariç
                lang_name = TranslationManager.get_language_name(lang_code)
                
                for field_name in required_fields:
                    translation_field = f'{field_name}_{lang_code}'
                    value = cleaned_data.get(translation_field)
                    
                    # Boş değer kontrolü
                    if not value or (isinstance(value, str) and not value.strip()):
                        validation_errors[translation_field] = f'{field_name.title()} {lang_name} çevirisi zorunludur.'
        
        if validation_errors:
            raise ValidationError(validation_errors)
            
        return cleaned_data


class TranslationFieldBuilder:
    """Dinamik çeviri alanları oluşturan sınıf"""
    
    @staticmethod
    def build_widget_attrs(base_attrs, placeholder, lang_name):
        """Widget attributes'ları oluştur"""
        from .constants import FORM_WIDGET_CLASSES
        
        attrs = base_attrs.copy()
        attrs.update({
            'class': f'{attrs.get("class", FORM_WIDGET_CLASSES["text"])} required-translation'.strip(),
            'placeholder': f'{placeholder} ({lang_name}) - Zorunlu'
        })
        return attrs
    
    @staticmethod
    def create_translation_field(field_config, lang_code, enabled_languages):
        """Tek bir çeviri alanı oluştur"""
        from django import forms
        from django_ckeditor_5.widgets import CKEditor5Widget
        
        if lang_code == 'tr' or lang_code not in enabled_languages:
            return None
            
        lang_name = TranslationManager.get_language_name(lang_code)
        
        # Widget'ı belirle
        widget_class = field_config.get('widget', forms.TextInput)
        widget_attrs = field_config.get('widget_attrs', {})
        
        # Placeholder oluştur
        placeholder = field_config.get('placeholder', field_config.get('label', ''))
        
        # Widget attributes'ları hazırla
        final_attrs = TranslationFieldBuilder.build_widget_attrs(
            widget_attrs, placeholder, lang_name
        )
        
        # Widget instance oluştur
        if widget_class == CKEditor5Widget:
            widget_instance = CKEditor5Widget(
                config_name=widget_attrs.get('config_name', 'default'), 
                attrs=final_attrs
            )
        else:
            widget_instance = widget_class(attrs=final_attrs)
        
        # Field oluştur
        field = forms.CharField(
            label=f'{field_config["label"]} ({lang_name})',
            required=field_config.get('required', False),
            widget=widget_instance,
            help_text=f'{field_config["label"]} için {lang_name} çevirisi'
        )
        
        return field