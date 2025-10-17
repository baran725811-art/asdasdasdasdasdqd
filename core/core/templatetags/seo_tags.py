# core\core\templatetags\seo_tags.py - HATA DÜZELTİLMİŞ

# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.db.models import Q, Count
from django.urls import reverse
import re
import json

register = template.Library()

@register.simple_tag
def related_products(current_product, limit=4):
    """Related products"""
    try:
        from products.models import Product
        
        if not current_product:
            return Product.objects.filter(is_active=True, is_featured=True)[:limit]
        
        # Same category products
        related = Product.objects.filter(
            category=current_product.category,
            is_active=True
        ).exclude(pk=current_product.pk)
        
        if related.count() < limit:
            additional = Product.objects.filter(
                is_active=True,
                is_featured=True
            ).exclude(pk=current_product.pk).exclude(
                pk__in=related.values_list('pk', flat=True)
            )
            
            related_ids = list(related.values_list('pk', flat=True))
            additional_ids = list(additional.values_list('pk', flat=True))
            all_ids = (related_ids + additional_ids)[:limit]
            
            return Product.objects.filter(pk__in=all_ids)
        
        return related[:limit]
        
    except Exception:
        return []

@register.simple_tag
def smart_internal_links(content, max_links=5):
    """Smart internal links"""
    if not content:
        return content
    
    try:
        from products.models import Product, Category
        
        cache_key = 'internal_link_keywords'
        keywords = cache.get(cache_key)
        
        if keywords is None:
            keywords = {}
            
            # Product keywords
            products = Product.objects.filter(is_active=True).values('name', 'slug')
            for product in products:
                keywords[product['name'].lower()] = reverse('products:product_detail', kwargs={'slug': product['slug']})
            
            # Category keywords
            categories = Category.objects.filter(is_active=True).values('name', 'slug')
            for category in categories:
                keywords[category['name'].lower()] = reverse('products:category_detail', kwargs={'slug': category['slug']})
            
            cache.set(cache_key, keywords, 3600)
        
        # Link keywords in content
        linked_content = content
        link_count = 0
        
        for keyword, url in keywords.items():
            if link_count >= max_links:
                break
                
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            
            if pattern.search(linked_content) and '<a' not in linked_content.lower():
                linked_content = pattern.sub(
                    f'<a href="{url}" class="internal-link">{keyword}</a>',
                    linked_content,
                    count=1
                )
                link_count += 1
        
        return mark_safe(linked_content)
        
    except Exception:
        return content

@register.simple_tag
def seo_meta_robots(page_type="default"):
    """SEO robots meta tag"""
    robots_map = {
        'home': 'index, follow',
        'product': 'index, follow',
        'category': 'index, follow',
        'gallery': 'index, follow',
        'about': 'index, follow',
        'contact': 'index, follow',
        'search': 'noindex, follow',
        'login': 'noindex, nofollow',
        'admin': 'noindex, nofollow',
        'error': 'noindex, nofollow',
        'draft': 'noindex, nofollow'
    }
    
    return robots_map.get(page_type, 'index, follow')

@register.simple_tag(takes_context=True)
def canonical_url(context, custom_url=None):
    """Canonical URL"""
    request = context['request']
    
    if custom_url:
        return f"{request.scheme}://{request.get_host()}{custom_url}"
    
    return f"{request.scheme}://{request.get_host()}{request.path}"

@register.simple_tag
def og_image_url(image_obj=None, default_image=None):
    """Open Graph image URL"""
    if image_obj and hasattr(image_obj, 'url'):
        return image_obj.url
    elif default_image:
        return default_image
    else:
        return '/static/images/og-default.jpg'

@register.simple_tag
def json_ld_website(site_name, site_url, description=""):
    """Website JSON-LD schema"""
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": site_url,
        "description": description,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{site_url}/urunler/?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')

@register.simple_tag
def json_ld_organization(name, url, logo_url, phone="", email="", address=""):
    """Organization JSON-LD schema"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": url,
        "logo": logo_url
    }
    
    if phone:
        schema["telephone"] = phone
    if email:
        schema["email"] = email
    if address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": address
        }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')

@register.simple_tag
def reading_time(content):
    """Reading time calculation"""
    if not content:
        return 0
    
    clean_text = re.sub(r'<[^>]+>', '', content)
    word_count = len(clean_text.split())
    
    reading_minutes = max(1, round(word_count / 200))
    
    return reading_minutes

@register.simple_tag
def content_length(content):
    """Content length"""
    if not content:
        return 0
    
    clean_text = re.sub(r'<[^>]+>', '', content)
    return len(clean_text)

@register.filter
def meta_description_optimize(text, max_length=160):
    """Optimize meta description"""
    if not text:
        return ""
    
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    if len(clean_text) <= max_length:
        return clean_text
    
    truncated = clean_text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:
        return truncated[:last_space] + '...'
    else:
        return truncated + '...'

@register.simple_tag
def page_load_time():
    """Page load time script"""
    return mark_safe(
        '<script>window.addEventListener("load", function(){console.log("Page loaded in:", performance.now(), "ms");});</script>'
    )

@register.simple_tag(takes_context=True)
def similar_pages(context, current_url, limit=5):
    """Similar pages"""
    try:
        if '/urunler/' in current_url:
            from products.models import Product
            products = Product.objects.filter(is_active=True)[:limit]
            return [{'title': p.name, 'url': p.get_absolute_url()} for p in products]
        
        elif '/galeri/' in current_url:
            from gallery.models import Gallery
            items = Gallery.objects.filter(is_active=True)[:limit]
            return [{'title': i.title, 'url': i.get_absolute_url()} for i in items]
        
        return []
        
    except Exception:
        return []

@register.simple_tag
def preload_critical_resources():
    """Critical resources preload"""
    preloads = [
        '<link rel="preload" href="/static/css/style.css" as="style">',
        '<link rel="preload" href="/static/js/main.js" as="script">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://res.cloudinary.com">',
    ]
    
    return mark_safe('\n'.join(preloads))