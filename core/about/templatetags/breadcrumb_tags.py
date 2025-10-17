# core/templatetags/breadcrumb_tags.py - YENİ DOSYA OLUŞTUR

from django import template
from django.urls import resolve, Resolver404
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.simple_tag(takes_context=True)
def breadcrumb_json_ld(context):
    """
    Breadcrumb için JSON-LD structured data oluşturur
    """
    request = context['request']
    breadcrumbs = context.get('breadcrumbs', [])
    
    if not breadcrumbs or len(breadcrumbs) <= 1:
        return ''
    
    # Sadece current olmayan breadcrumb'ları al
    valid_breadcrumbs = [b for b in breadcrumbs if not b.get('is_current', False)]
    
    if not valid_breadcrumbs:
        return ''
    
    structured_data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for i, breadcrumb in enumerate(valid_breadcrumbs):
        structured_data["itemListElement"].append({
            "@type": "ListItem",
            "position": i + 1,
            "name": breadcrumb['name'],
            "item": f"{request.scheme}://{request.get_host()}{breadcrumb['url']}"
        })
    
    json_str = json.dumps(structured_data, ensure_ascii=False, indent=2)
    return mark_safe(f'<script type="application/ld+json">\n{json_str}\n</script>')

@register.inclusion_tag('includes/breadcrumb.html', takes_context=True)
def render_breadcrumb(context, show_home_icon=True, separator="chevron"):
    """
    Breadcrumb render etmek için inclusion tag
    
    Args:
        show_home_icon: Ana sayfa ikonu göster/gizle
        separator: Ayırıcı tipi (chevron, slash, arrow)
    """
    breadcrumbs = context.get('breadcrumbs', [])
    
    # Separator ikonları
    separator_icons = {
        'chevron': 'fa-chevron-right',
        'slash': 'fa-slash',
        'arrow': 'fa-arrow-right',
        'angle': 'fa-angle-right'
    }
    
    return {
        'breadcrumbs': breadcrumbs,
        'show_home_icon': show_home_icon,
        'separator_icon': separator_icons.get(separator, 'fa-chevron-right'),
        'request': context['request']
    }

@register.simple_tag
def breadcrumb_separator(separator_type="chevron"):
    """
    Breadcrumb ayırıcısı için ikon döndürür
    """
    icons = {
        'chevron': '<i class="fas fa-chevron-right"></i>',
        'slash': '<i class="fas fa-slash"></i>',
        'arrow': '<i class="fas fa-arrow-right"></i>',
        'angle': '<i class="fas fa-angle-right"></i>',
        'double-angle': '<i class="fas fa-angle-double-right"></i>'
    }
    
    return mark_safe(icons.get(separator_type, icons['chevron']))

@register.filter
def truncate_breadcrumb(value, max_length=30):
    """
    Breadcrumb ismini belirli uzunlukta kısaltır
    """
    if not value or len(value) <= max_length:
        return value
    
    return value[:max_length-3] + '...'

@register.simple_tag(takes_context=True)
def current_page_title(context):
    """
    Mevcut sayfa başlığını breadcrumb'dan al
    """
    breadcrumbs = context.get('breadcrumbs', [])
    
    for breadcrumb in reversed(breadcrumbs):
        if breadcrumb.get('is_current', False):
            return breadcrumb['name']
    
    return _('Sayfa')

@register.simple_tag(takes_context=True)
def parent_page_url(context):
    """
    Üst sayfa URL'ini döndürür
    """
    breadcrumbs = context.get('breadcrumbs', [])
    
    if len(breadcrumbs) >= 2:
        # Son iki öğeyi al, son öncekinin URL'ini döndür
        parent = breadcrumbs[-2]
        return parent['url']
    
    return '/'

@register.simple_tag(takes_context=True)
def breadcrumb_path_array(context):
    """
    Breadcrumb path'ini array olarak döndürür (JavaScript için)
    """
    breadcrumbs = context.get('breadcrumbs', [])
    
    path_array = []
    for breadcrumb in breadcrumbs:
        path_array.append({
            'name': breadcrumb['name'],
            'url': breadcrumb['url'],
            'isCurrent': breadcrumb.get('is_current', False)
        })
    
    return mark_safe(json.dumps(path_array, ensure_ascii=False))

@register.inclusion_tag('includes/mobile_breadcrumb.html', takes_context=True)
def mobile_breadcrumb(context):
    """
    Mobile için kompakt breadcrumb
    """
    breadcrumbs = context.get('breadcrumbs', [])
    
    # Mobile için sadece son 2-3 breadcrumb göster
    if len(breadcrumbs) > 3:
        mobile_breadcrumbs = [breadcrumbs[0]] + breadcrumbs[-2:]
        show_ellipsis = True
    else:
        mobile_breadcrumbs = breadcrumbs
        show_ellipsis = False
    
    return {
        'breadcrumbs': mobile_breadcrumbs,
        'show_ellipsis': show_ellipsis,
        'total_count': len(breadcrumbs),
        'request': context['request']
    }