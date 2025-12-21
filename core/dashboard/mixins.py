# dashboard/mixins.py
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget
from django.contrib import messages

from .constants import TRANSLATION_REQUIRED_FIELDS, LANGUAGE_NAMES, FORM_WIDGET_CLASSES
from .translation_utils import TranslationManager, TranslationFieldBuilder


class TranslationViewMixin:
    """View'lar için çeviri işlemlerini yöneten mixin"""
    
    def get_translation_context(self):
        """Çeviri context'ini hazırla"""
        translation_data = TranslationManager.get_user_translation_settings(self.request.user)
        return {
            'translation_enabled': translation_data['translation_enabled'],
            'enabled_languages': translation_data['enabled_languages'], 
            'user_translation_settings': translation_data['user_translation_settings'],
        }
    
    def handle_translation_form_errors(self, form):
        """Form çeviri hatalarını işle"""
        translation_context = self.get_translation_context()
        return TranslationManager.handle_translation_form_errors(
            form, 
            translation_context['enabled_languages'], 
            self.request
        )
    
    def get_form_kwargs(self):
        """Form kwargs'larına çeviri bilgilerini ekle"""
        kwargs = super().get_form_kwargs() if hasattr(super(), 'get_form_kwargs') else {}
        translation_context = self.get_translation_context()
        kwargs.update(translation_context)
        kwargs['user'] = self.request.user
        return kwargs


class RequiredTranslationMixin:
    """
    Form'larda çeviri alanlarını zorunlu yapar - KESIN ÇÖZÜM
    """
    
    def __init__(self, *args, **kwargs):
        # Çeviri parametrelerini al
        self.translation_enabled = kwargs.pop('translation_enabled', False)
        self.enabled_languages = kwargs.pop('enabled_languages', ['tr'])
        self.user = kwargs.pop('user', None)
        kwargs.pop('user_translation_settings', None)

        super().__init__(*args, **kwargs)
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._setup_required_translation_fields()
    
    def _setup_required_translation_fields(self):
        """Seçilen diller için çeviri alanlarını zorunlu yap"""
        model_name = self._meta.model.__name__
        required_fields = TRANSLATION_REQUIRED_FIELDS.get(model_name, [])
        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':  # Ana dil hariç
                for field_name in required_fields:
                    translation_field = f'{field_name}_{lang_code}'
                    if translation_field in self.fields:
                        # Alan zorunlu yap
                        self.fields[translation_field].required = True
                        
                        # CSS class ekle (görsel işaret için)
                        widget = self.fields[translation_field].widget
                        css_classes = widget.attrs.get('class', '')
                        widget.attrs['class'] = f'{css_classes} required-translation'.strip()
                        
                        # Placeholder güncelle
                        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                        original_label = self.fields[field_name].label if field_name in self.fields else field_name
                        widget.attrs['placeholder'] = f'{original_label} ({lang_name}) - Zorunlu'
    
    def clean(self):
        """KESIN ÇÖZÜM: Çeviri alanlarını cleaned_data'ya ekle"""
        cleaned_data = super().clean()
        
        # Çeviri alanlarını cleaned_data'ya dahil et
        if self.translation_enabled and len(self.enabled_languages) > 1:
            translation_fields = self._get_model_translation_fields()
            
            for lang_code in self.enabled_languages:
                if lang_code != 'tr':
                    for field_name in translation_fields:
                        translation_field_name = f'{field_name}_{lang_code}'
                        if translation_field_name in self.data:
                            # Form data'sından çeviri alanının değerini al
                            field_value = self.data.get(translation_field_name, '').strip()
                            cleaned_data[translation_field_name] = field_value
        
        return cleaned_data
    
    def _get_model_translation_fields(self):
        """Model'e göre çeviri alanlarını döndür"""
        model_name = self._meta.model.__name__
        
        translation_fields_map = {
            'Gallery': ['title', 'description', 'alt_text'],
            'Product': ['name', 'description', 'meta_title', 'meta_description'],
            'Category': ['name', 'description', 'meta_title', 'meta_description'],
            'Service': ['title', 'description'],
            'TeamMember': ['name', 'position', 'bio'],
            'CarouselSlide': ['title', 'description', 'alt_text', 'button_text'],
            'MediaMention': ['title', 'source', 'description']
        }
        
        return translation_fields_map.get(model_name, [])


class TranslationFieldGenerator:
    """Çeviri alanlarını dinamik olarak oluşturan yardımcı sınıf"""
    
    @staticmethod
    def add_translation_fields(form_instance, field_configs, enabled_languages):
        """Form'a çeviri alanlarını ekle"""
        
        for lang_code in enabled_languages:
            if lang_code != 'tr':  # Ana dil hariç
                
                for field_name, config in field_configs.items():
                    translation_field_name = f'{field_name}_{lang_code}'
                    
                    # Çeviri alanı oluştur
                    translation_field = TranslationFieldBuilder.create_translation_field(
                        config, lang_code, enabled_languages
                    )
                    
                    if translation_field:
                        form_instance.fields[translation_field_name] = translation_field


class BaseTranslationForm(RequiredTranslationMixin, forms.ModelForm):
    """
    Tüm çeviri form'ları için temel sınıf - KESIN ÇÖZÜM
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_widget_classes()
        
        # Çeviri alanları için initial değerlerini ayarla
        if hasattr(self, 'instance') and self.instance.pk and self.translation_enabled:
            self._set_translation_initial_values()
    
    def _apply_base_widget_classes(self):
        """Tüm alanlara ortak CSS class'larını uygula"""
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Widget tipine göre CSS class belirle
            if isinstance(widget, forms.TextInput):
                css_class = FORM_WIDGET_CLASSES['text']
            elif isinstance(widget, forms.Textarea):
                css_class = FORM_WIDGET_CLASSES['textarea']
            elif isinstance(widget, forms.Select):
                css_class = FORM_WIDGET_CLASSES['select']
            elif isinstance(widget, forms.CheckboxInput):
                css_class = FORM_WIDGET_CLASSES['checkbox']
            elif isinstance(widget, forms.FileInput):
                css_class = FORM_WIDGET_CLASSES['file']
            elif isinstance(widget, forms.DateInput):
                css_class = FORM_WIDGET_CLASSES['date']
            elif isinstance(widget, forms.NumberInput):
                css_class = FORM_WIDGET_CLASSES['number']
            elif isinstance(widget, forms.URLInput):
                css_class = FORM_WIDGET_CLASSES['url']
            elif isinstance(widget, forms.EmailInput):
                css_class = FORM_WIDGET_CLASSES['email']
            else:
                css_class = FORM_WIDGET_CLASSES['text']  # Varsayılan
            
            # Mevcut class'ları koru, yeni class'ı ekle
            existing_class = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing_class} {css_class}'.strip()
    
    def _set_translation_initial_values(self):
        """Edit modunda çeviri alanlarının initial değerlerini ayarla"""
        translation_fields = self._get_model_translation_fields()
        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                for field_name in translation_fields:
                    translation_field_name = f'{field_name}_{lang_code}'
                    if translation_field_name in self.fields:
                        # Instance'dan çeviri değerini al
                        translation_value = getattr(self.instance, translation_field_name, '')
                        self.fields[translation_field_name].initial = translation_value or ''
    
    def _get_model_translation_fields(self):
        """Model'e göre çeviri alanlarını döndür"""
        model_name = self._meta.model.__name__
        
        translation_fields_map = {
            'Gallery': ['title', 'description', 'alt_text'],
            'Product': ['name', 'description', 'meta_title', 'meta_description'],
            'Category': ['name', 'description', 'meta_title', 'meta_description'],
            'Service': ['title', 'description'],
            'TeamMember': ['name', 'position', 'bio'],
            'CarouselSlide': ['title', 'description', 'alt_text', 'button_text'],
            'MediaMention': ['title', 'source', 'description']
        }
        
        return translation_fields_map.get(model_name, [])


class StaffRequiredMixin:
    """Staff yetkisi kontrolü için mixin"""

    def dispatch(self, request, *args, **kwargs):
        from django.contrib.admin.views.decorators import staff_member_required
        from django.utils.decorators import method_decorator

        @method_decorator(staff_member_required(login_url='dashboard:dashboard_login'))
        def wrapper(view_func):
            return view_func

        return wrapper(super().dispatch)(request, *args, **kwargs)


class AutoOrderMixin(models.Model):
    """
    Otomatik sıralama işlevselliği sağlayan mixin

    Kullanım:
        class MyModel(AutoOrderMixin, models.Model):
            # order field'ı otomatik olarak yönetilir
            pass

    Özellikler:
        - Yeni kayıt order belirtilmezse → en sona ekler
        - Yeni kayıt order=1 gibi belirtilirse → diğer kayıtları kaydırır
        - Mevcut kayıt order'ı değiştirilirse → diğer kayıtları yeniden sıralar
        - Transaction-safe (atomik işlem)
        - Toplu güncelleme ile performanslı
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from django.db import transaction

        with transaction.atomic():
            # Model'in order field'ını kontrol et
            if not hasattr(self, 'order'):
                raise AttributeError(
                    f"{self.__class__.__name__} model'inde 'order' field'ı bulunamadı. "
                    "AutoOrderMixin kullanmak için model'de 'order' field'ı olmalıdır."
                )

            # Yeni kayıt mı yoksa güncelleme mi?
            is_new = self.pk is None

            if is_new:
                # YENİ KAYIT
                if self.order is None or self.order == 0:
                    # SENARYO 1: Order belirtilmemiş → en sona ekle
                    max_order = self.__class__.objects.aggregate(
                        models.Max('order')
                    )['order__max'] or 0
                    self.order = max_order + 1
                else:
                    # SENARYO 2: Order belirtilmiş → diğerlerini kaydır
                    # Belirtilen order'dan büyük veya eşit olan tüm kayıtları 1 arttır
                    self.__class__.objects.filter(
                        order__gte=self.order
                    ).update(order=models.F('order') + 1)
            else:
                # MEVCUT KAYDIN GÜNCELLENMESİ
                # Eski order değerini al
                try:
                    old_instance = self.__class__.objects.get(pk=self.pk)
                    old_order = old_instance.order

                    if old_order != self.order:
                        # SENARYO 3: Order değiştirilmiş → yeniden sırala

                        if self.order > old_order:
                            # Order arttırılmış → aradaki kayıtları 1 azalt
                            self.__class__.objects.filter(
                                order__gt=old_order,
                                order__lte=self.order
                            ).exclude(pk=self.pk).update(order=models.F('order') - 1)
                        else:
                            # Order azaltılmış → aradaki kayıtları 1 arttır
                            self.__class__.objects.filter(
                                order__gte=self.order,
                                order__lt=old_order
                            ).exclude(pk=self.pk).update(order=models.F('order') + 1)

                except self.__class__.DoesNotExist:
                    # Eski kayıt bulunamadı (olağandışı durum)
                    pass

            # Kaydı kaydet
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Kayıt silindiğinde diğer kayıtların order'larını düzenle
        """
        from django.db import transaction

        with transaction.atomic():
            deleted_order = self.order

            # Kaydı sil
            super().delete(*args, **kwargs)

            # Silinen order'dan büyük olan tüm kayıtları 1 azalt
            self.__class__.objects.filter(
                order__gt=deleted_order
            ).update(order=models.F('order') - 1)