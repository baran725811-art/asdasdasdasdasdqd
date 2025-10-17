# dashboard/templatetags/dashboard_filters.py 

from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Dictionary'den key'e göre değer döndürür.
    Kullanım: {{ dict|lookup:key }}
    """
    if not dictionary or not key:
        return None
    
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    
    # Eğer dictionary bir object ise attribute olarak erişmeyi dene
    try:
        return getattr(dictionary, str(key), None)
    except (AttributeError, TypeError):
        return None

# YENİ EKLENEN FONKSİYONLAR:

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Mevcut URL parametrelerini koruyarak yeni parametreler ekler/değiştirir
    Kullanım: {% url_replace page=2 %}
    """
    request = context['request']
    params = request.GET.copy()
    
    for key, value in kwargs.items():
        if value is None or value == '':
            if key in params:
                del params[key]
        else:
            params[key] = value
    
    return '?' + params.urlencode() if params else ''

@register.simple_tag
def url_params(**kwargs):
    """
    URL parametrelerini string olarak döndürür
    Kullanım: {% url_params page=2 category=3 %}
    """
    return '?' + urlencode({k: v for k, v in kwargs.items() if v is not None and v != ''})

@register.filter
def add_url_param(url, param):
    """
    URL'ye parametre ekler
    Kullanım: {{ request.get_full_path|add_url_param:"page=2" }}
    """
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}{param}"