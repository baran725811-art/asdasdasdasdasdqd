# core/templatetags/image_tags.py - KURAL UYUMLU VERSİYON

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()

@register.simple_tag
def optimized_image(image_field, size_type='default', alt_text='', css_class='', **kwargs):
    """
    Optimized image tag for different sections
    Usage: {% optimized_image item.image 'gallery' alt_text=item.alt_text css_class='img-fluid' %}
    """
    if not image_field:
        return ''
    
    # Size type'a göre boyutları belirle
    size_configs = {
        'carousel': {'width': 1920, 'height': 1080},
        'gallery': {'width': 800, 'height': 600},
        'gallery_thumb': {'width': 400, 'height': 300},
        'products': {'width': 600, 'height': 400},
        'products_thumb': {'width': 300, 'height': 200},
        'categories': {'width': 400, 'height': 250},
        'about': {'width': 800, 'height': 600},
        'services': {'width': 400, 'height': 250},
        'team': {'width': 300, 'height': 300},
        'reviews': {'width': 100, 'height': 100},
        'media': {'width': 400, 'height': 250},
        'logo': {'width': 200, 'height': 60},
        'logo_small': {'width': 60, 'height': 60},
        'default': {'width': 800, 'height': 600}
    }
    
    config = size_configs.get(size_type, size_configs['default'])
    
    # Cloudinary URL oluştur
    image_url = ''
    if hasattr(image_field, 'url') and image_field.url:
        base_url = image_field.url
        if '/upload/' in base_url:
            parts = base_url.split('/upload/')
            if len(parts) == 2:
                # Normal auto gravity
                image_url = f"{parts[0]}/upload/w_{config['width']},h_{config['height']},c_fill,g_auto,q_auto:good,f_auto/{parts[1]}"
            else:
                image_url = base_url
        else:
            image_url = base_url
    else:
        image_url = image_field.url if image_field else ''
    
    if not image_url:
        return ''
    
    # HTML oluştur
    html = f'<img src="{image_url}" alt="{alt_text}"'
    
    if css_class:
        html += f' class="{css_class}"'
    
    # Loading lazy ekle (carousel hariç)
    if size_type != 'carousel':
        html += ' loading="lazy"'
    
    html += '>'
    
    return mark_safe(html)


@register.simple_tag
def original_image_url(image_field, max_width=1200, max_height=800):
    """
    Modal için orijinal tam boyut resim URL'i (kırpılmamış)
    SADECE Gallery ve Products için kullanılabilir
    Usage: {% original_image_url item.image %}
    """
    if not image_field:
        return ''
    
    if hasattr(image_field, 'url') and image_field.url:
        base_url = image_field.url
        if '/upload/' in base_url:
            parts = base_url.split('/upload/')
            if len(parts) == 2:
                # Orijinal boyut limiti ile, kırpma yok
                return f"{parts[0]}/upload/w_{max_width},h_{max_height},c_limit,q_auto:good,f_auto/{parts[1]}"
    
    return image_field.url if image_field else ''


@register.simple_tag  
def cropped_image_url(image_field, size_type='default'):
    """
    Kırpılmış resim URL'i (kartlar için)
    Usage: {% cropped_image_url item.cropped_image 'gallery' %}
    """
    if not image_field:
        return ''
    
    # Boyut ayarları
    size_configs = {
        'gallery': {'width': 400, 'height': 300},
        'products': {'width': 300, 'height': 200},
        'products_main': {'width': 600, 'height': 500},
        'about': {'width': 400, 'height': 300},
        'services': {'width': 400, 'height': 250},
        'team': {'width': 250, 'height': 250},
        'carousel': {'width': 800, 'height': 450},
        'default': {'width': 400, 'height': 300}
    }
    
    config = size_configs.get(size_type, size_configs['default'])
    
    if hasattr(image_field, 'url') and image_field.url:
        base_url = image_field.url
        if '/upload/' in base_url:
            parts = base_url.split('/upload/')
            if len(parts) == 2:
                return f"{parts[0]}/upload/w_{config['width']},h_{config['height']},c_fill,g_auto,q_auto:good,f_auto/{parts[1]}"
    
    return image_field.url if image_field else ''


# ===== GALLERY & PRODUCTS BÖLÜMÜ (Hem orijinal hem kırpılmış kullanılabilir) =====

@register.simple_tag
def gallery_card_image(gallery_obj, css_class=''):
    """
    Gallery kartları için resim tag'i (kırpılmış öncelikli, fallback orijinal)
    Usage: {% gallery_card_image gallery_item 'img-fluid' %}
    """
    if not gallery_obj:
        return ''
    
    # Kırpılmış resim varsa onu kullan
    image_url = ''
    alt_text = gallery_obj.get_alt_text() if hasattr(gallery_obj, 'get_alt_text') else gallery_obj.alt_text or ''
    
    if gallery_obj.cropped_image:
        image_url = cropped_image_url(gallery_obj.cropped_image, 'gallery')
    elif gallery_obj.image:
        # Fallback: orijinal resmi kırparak kullan
        image_url = cropped_image_url(gallery_obj.image, 'gallery')
    
    if not image_url:
        return ''
    
    html = f'<img src="{image_url}" alt="{alt_text}"'
    if css_class:
        html += f' class="{css_class}"'
    html += ' loading="lazy">'
    
    return mark_safe(html)


@register.simple_tag  
def gallery_modal_image(gallery_obj, css_class=''):
    """
    Gallery modal için tam boyut resim tag'i (orijinal)
    Usage: {% gallery_modal_image gallery_item 'modal-image' %}
    """
    if not gallery_obj or not gallery_obj.image:
        return ''
    
    alt_text = gallery_obj.get_alt_text() if hasattr(gallery_obj, 'get_alt_text') else gallery_obj.alt_text or ''
    image_url = original_image_url(gallery_obj.image)
    
    if not image_url:
        return ''
    
    html = f'<img src="{image_url}" alt="{alt_text}"'
    if css_class:
        html += f' class="{css_class}"'
    html += ' loading="lazy">'
    
    return mark_safe(html)


@register.simple_tag
def product_card_image(product_obj, css_class=''):
    """
    Product kartları için resim tag'i (kırpılmış öncelikli, orijinal ortalanarak fallback)
    Usage: {% product_card_image product_item 'img-fluid' %}
    """
    if not product_obj:
        return ''
    
    image_url = ''
    alt_text = product_obj.get_alt_text() if hasattr(product_obj, 'get_alt_text') else product_obj.alt_text or ''
    additional_class = ''
    
    size_type = 'products_main' if 'main-product-image' in css_class else 'products'

    if product_obj.cropped_image:
        # Kırpılmış resim varsa onu kullan
        image_url = cropped_image_url(product_obj.cropped_image, size_type)
    elif product_obj.image:
        # Fallback: orijinal resmi kırparak göster
        image_url = cropped_image_url(product_obj.image, size_type)
        additional_class = ' centered-fallback'
    
    if not image_url:
        return ''
    
    final_class = css_class + additional_class
    html = f'<img src="{image_url}" alt="{alt_text}"'
    if final_class.strip():
        html += f' class="{final_class.strip()}"'
    html += ' loading="lazy">'
    
    return mark_safe(html)


@register.simple_tag
def product_modal_image(product_obj, css_class=''):
    """
    Product modal için tam boyut resim tag'i (orijinal)
    Usage: {% product_modal_image product_item 'modal-image' %}
    """
    if not product_obj or not product_obj.image:
        return ''
    
    alt_text = product_obj.get_alt_text() if hasattr(product_obj, 'get_alt_text') else product_obj.alt_text or ''
    image_url = original_image_url(product_obj.image)
    
    if not image_url:
        return ''
    
    html = f'<img src="{image_url}" alt="{alt_text}"'
    if css_class:
        html += f' class="{css_class}"'
    html += ' loading="lazy">'
    
    return mark_safe(html)


# ===== CAROUSEL/TEAM/ABOUT/SERVICES BÖLÜMÜ (Sadece kırpılmış kullanılacak) =====

@register.simple_tag
def about_card_image(obj, css_class=''):
    """
    About/Service/Team kartları için resim tag'i - SADECE KIRPILMIŞ
    Usage: {% about_card_image service_item 'img-fluid' %}
    """
    if not obj:
        return ''
    
    # Obje tipine göre size_type belirle
    size_type = 'about'
    if hasattr(obj, '_meta'):
        model_name = obj._meta.model_name.lower()
        if model_name == 'service':
            size_type = 'services'
        elif model_name == 'teammember':
            size_type = 'team'
    
    image_url = ''
    alt_text = obj.get_alt_text() if hasattr(obj, 'get_alt_text') else obj.alt_text or ''
    
    # SADECE kırpılmış resim kullan - orijinal fallback YOK
    if obj.cropped_image:
        image_url = cropped_image_url(obj.cropped_image, size_type)
    
    if not image_url:
        return ''
    
    html = f'<img src="{image_url}" alt="{alt_text}"'
    if css_class:
        html += f' class="{css_class}"'
    html += ' loading="lazy">'
    
    return mark_safe(html)


@register.simple_tag
def carousel_image(slide_obj, css_class='', is_first=False, alt_text=''):
    """
    Carousel için resim tag'i
    Usage: {% carousel_image slide 'carousel-image' is_first=forloop.first alt_text=slide.alt_text %}
    """
    if not slide_obj:
        return ''
    
    # Loading ayarları
    loading = 'eager' if is_first else 'lazy'
    fetchpriority = 'high' if is_first else None
    
    image_url = ''
    # Alt text önceliği: parametre > obje metodu > obje attr > boş
    if alt_text:
        final_alt_text = alt_text
    elif hasattr(slide_obj, 'get_alt_text'):
        final_alt_text = slide_obj.get_alt_text() or ''
    elif hasattr(slide_obj, 'alt_text'):
        final_alt_text = slide_obj.alt_text or ''
    else:
        final_alt_text = ''
    
    # Image alanını kullan
    if slide_obj.image:  # ← cropped_image yerine image
        image_url = cropped_image_url(slide_obj.image, 'carousel')  # ← cropped_image yerine image
    
    if not image_url:
        return ''
    
    html = f'<img src="{image_url}" alt="{final_alt_text}"'
    if css_class:
        html += f' class="{css_class}"'
    html += f' loading="{loading}"'
    if fetchpriority:
        html += f' fetchpriority="{fetchpriority}"'
    html += '>'
    
    return mark_safe(html)


@register.simple_tag
def team_image(team_obj, css_class=''):
    """
    Team için özel resim tag'i - SADECE KIRPILMIŞ
    Usage: {% team_image team_member 'team-image' %}
    """
    if not team_obj:
        return ''
    
    image_url = ''
    alt_text = team_obj.get_alt_text() if hasattr(team_obj, 'get_alt_text') else team_obj.alt_text or ''
    
    # SADECE kırpılmış resim kullan - orijinal fallback YOK
    if team_obj.cropped_image:
        image_url = cropped_image_url(team_obj.cropped_image, 'team')
    
    if not image_url:
        return ''
    
    html = f'<img src="{image_url}" alt="{alt_text}"'
    if css_class:
        html += f' class="{css_class}"'
    html += ' loading="lazy">'
    
    return mark_safe(html)


@register.simple_tag
def service_image(service_obj, css_class=''):
    """
    Service için özel resim tag'i - SADECE KIRPILMIŞ
    Usage: {% service_image service_item 'service-image' %}
    """
    if not service_obj:
        return ''
    
    image_url = ''
    alt_text = service_obj.get_alt_text() if hasattr(service_obj, 'get_alt_text') else service_obj.alt_text or ''
    
    # SADECE kırpılmış resim kullan - orijinal fallback YOK
    if service_obj.cropped_image:
        image_url = cropped_image_url(service_obj.cropped_image, 'services')
    
    if not image_url:
        return ''
    
    html = f'<img src="{image_url}" alt="{alt_text}"'
    if css_class:
        html += f' class="{css_class}"'
    html += ' loading="lazy">'
    
    return mark_safe(html)


# ===== YARDIMCI FONKSİYONLAR =====

@register.filter
def get_image_dimensions(size_type):
    """
    Boyut tipine göre genişlik/yükseklik döndürür
    Usage: {{ 'gallery'|get_image_dimensions }}
    """
    dimensions = {
        'carousel': '1920x1080',
        'gallery': '800x600',
        'products': '600x400',
        'categories': '400x250',
        'about': '800x600',
        'services': '400x250',
        'team': '300x300',
        'reviews': '100x100',
        'media': '400x250',
        'logo': '200x60'
    }
    
    return dimensions.get(size_type, '800x600')


@register.simple_tag
def image_url_only(image_field, size_type='default'):
    """
    Sadece URL döndürür (JavaScript için)
    Usage: {% image_url_only item.image 'gallery' %}
    """
    if not image_field:
        return ''
    
    return cropped_image_url(image_field, size_type)