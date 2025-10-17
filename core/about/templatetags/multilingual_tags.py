# about/templatetags/multilingual_tags.py
from django import template
from django.utils.translation import get_language
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='get_translation')
def get_translation(obj, field_name):
    """Çok dilli alan değeri al"""
    current_lang = get_language()
    
    # Mevcut dil alanını dene
    lang_field = f"{field_name}_{current_lang}"
    if hasattr(obj, lang_field):
        value = getattr(obj, lang_field)
        if value and value.strip():
            return mark_safe(value)
    
    # Türkçe fallback
    tr_field = f"{field_name}_tr"
    if hasattr(obj, tr_field):
        value = getattr(obj, tr_field)
        if value and value.strip():
            return mark_safe(value)
    
    # İngilizce fallback
    en_field = f"{field_name}_en"
    if hasattr(obj, en_field):
        value = getattr(obj, en_field)
        if value and value.strip():
            return mark_safe(value)
    
    # Son çare - orijinal alan
    if hasattr(obj, field_name):
        value = getattr(obj, field_name)
        return mark_safe(value) if value else ''
    
    return ''