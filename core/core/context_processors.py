# core/context_processors.py 
from django.core.cache import cache
from .models import SiteSettings
from django.conf import settings
from .utils import check_cloudinary_storage  # YENİ EKLENEN
import logging

logger = logging.getLogger(__name__)

def seo_context(request):
    """
    Site ayarlarını VE ABOUT bilgilerini tüm template'lerde kullanılabilir hale getirir
    Cache kullanarak performansı optimize eder
    """
    
    # Cache'den site ayarlarını al
    site_settings = cache.get('site_settings')
    
    if site_settings is None:
        try:
            site_settings = SiteSettings.objects.get()
            cache.set('site_settings', site_settings, 60 * 15)  # 15 dakika cache
        except SiteSettings.DoesNotExist:
            site_settings = SiteSettings.objects.create()
            cache.set('site_settings', site_settings, 60 * 15)
    
    # ABOUT VERİLERİNİ DE CACHE'DEN AL
    about_info = cache.get('about_info')
    
    if about_info is None:
        try:
            from about.models import About
            about = About.objects.get(pk=1)
            about_info = {
                'title': about.title,
                'short_description': about.short_description,
                'mission': about.mission,
                'vision': about.vision,
                'story': about.story,
                'years_experience': about.years_experience,
                'completed_jobs': about.completed_jobs,
                'happy_customers': about.happy_customers,
                'total_services': about.total_services,
                'customer_satisfaction': about.customer_satisfaction,
                'meta_title': about.meta_title,
                'meta_description': about.meta_description,
                'image': about.image,
                'updated_at': about.updated_at,
            }
            cache.set('about_info', about_info, 60 * 10)  # 10 dakika cache
        except:
            # Varsayılan değerler
            about_info = {
                'title': 'Hakkımızda',
                'short_description': 'Profesyonel hizmet anlayışımızla sizlerleyiz.',
                'mission': 'Müşterilerimize en iyi hizmeti sunmak.',
                'vision': 'Sektörün lider firması olmak.',
                'story': 'Yıllardır süregelen deneyimimizle hizmet veriyoruz.',
                'years_experience': 20,
                'completed_jobs': 5000,
                'happy_customers': 1000,
                'total_services': 10,
                'customer_satisfaction': 100,
                'meta_title': '',
                'meta_description': '',
                'image': None,
                'updated_at': None,
            }
            cache.set('about_info', about_info, 60 * 10)

    # Kullanıcı dil ayarları
    user_primary_language = 'tr'
    if request.user.is_authenticated:
        try:
            from dashboard.models import DashboardTranslationSettings
            user_settings = DashboardTranslationSettings.objects.get(user=request.user)
            user_primary_language = user_settings.primary_language
        except:
            user_primary_language = 'tr'
    
    # Template context
    context = {
        # Site temel bilgileri
        'site_name': site_settings.site_name,
        'site_tagline': site_settings.site_tagline,
        'site_full_name': f"{site_settings.site_name} - {site_settings.site_tagline}",
        
        # SEO değerleri
        'seo_title': about_info.get('meta_title') or site_settings.seo_title,
        'seo_description': about_info.get('meta_description') or site_settings.seo_description,
        'seo_keywords': site_settings.seo_keywords,
        
        # Eski değişken isimleri (backward compatibility)
        'default_meta_description': site_settings.seo_description,
        'default_meta_keywords': site_settings.seo_keywords,
        
        # ABOUT BİLGİLERİ - YENİ EKLENEN
        'global_about': about_info,  # Tüm sayfalarda erişilebilir about bilgileri
        'about_title': about_info.get('title'),
        'about_mission': about_info.get('mission'),
        'about_vision': about_info.get('vision'),
        'company_years_experience': about_info.get('years_experience', 20),
        'company_completed_jobs': about_info.get('completed_jobs', 5000),
        'company_happy_customers': about_info.get('happy_customers', 1000),

        # COMPANY_INFO - Ana sayfa uyumluluğu için eklendi
        'company_info': {
            'years_experience': about_info.get('years_experience') or 20,
            'completed_jobs': about_info.get('completed_jobs') or 5000,
            'happy_customers': about_info.get('happy_customers') or 1000,
            'total_services': about_info.get('total_services') or 10,
            'customer_satisfaction': about_info.get('customer_satisfaction') or 100,
        },
        
        # Renk ayarları
        'primary_color': site_settings.primary_color,
        'secondary_color': site_settings.secondary_color,
        'navbar_color': site_settings.navbar_color,
        
        # Logo ve görseller
        'site_logo': site_settings.site_logo,
        'favicon': site_settings.favicon,
        
        # PDF Katalog
        'pdf_catalog_enabled': site_settings.pdf_catalog_enabled,
        'pdf_catalog_file': site_settings.pdf_catalog_file,
        'pdf_catalog_title': site_settings.pdf_catalog_title,
        
        # Sosyal medya
        'facebook_url': site_settings.facebook_url,
        'instagram_url': site_settings.instagram_url,
        'twitter_url': site_settings.twitter_url,
        'whatsapp_number': site_settings.whatsapp_number,
        'whatsapp_link': site_settings.get_whatsapp_link(),
        'youtube_url': site_settings.youtube_url,
        
        # İletişim bilgileri
        'contact_phone': site_settings.contact_phone,
        'contact_email': site_settings.contact_email,
        'contact_address': site_settings.contact_address,
        
        # Google Maps
        'google_maps_embed_url': site_settings.google_maps_embed_url,
        
        # Site ayarları objesi
        'site_settings': site_settings,
        
        # Çeviri sistemi
        'translation_enabled': site_settings.translation_enabled,
        
        # Sosyal medya kontrolleri
        'has_social_media': any([
            site_settings.facebook_url,
            site_settings.instagram_url,
            site_settings.twitter_url,
            site_settings.whatsapp_number,
            site_settings.youtube_url
        ]),
        
        # CSS için renk değişkenleri
        'css_colors': {
            'primary': site_settings.primary_color,
            'secondary': site_settings.secondary_color,
            'navbar': site_settings.navbar_color,
        },
        
        # Dil ayarları
        'current_language': request.LANGUAGE_CODE,
        'available_languages': settings.LANGUAGES,
        'dashboard_languages': getattr(settings, 'DASHBOARD_LANGUAGES', settings.LANGUAGES),
        'site_enabled_languages': get_site_enabled_languages(),
        'user_primary_language': user_primary_language,
        'site_primary_url': f'/{user_primary_language}/',
        
        # DEBUG BİLGİLERİ (sadece staff kullanıcılar için)
        'context_debug': {
            'about_cache_hit': about_info is not None,
            'about_updated_at': about_info.get('updated_at'),
            'site_settings_cache_hit': site_settings is not None,
        } if hasattr(request, 'user') and request.user.is_staff else None,
        
        'translation_enabled': site_settings.translation_enabled,
        'enabled_languages': get_site_enabled_languages(), 
        
        # PDF DEBUG BİLGİLERİ - YENİ EKLENEN (en sona ekle)
        'pdf_debug': {
            'pdf_catalog_enabled': site_settings.pdf_catalog_enabled,
            'pdf_catalog_file_exists': bool(site_settings.pdf_catalog_file),
            'pdf_catalog_file_url': site_settings.pdf_catalog_file.url if site_settings.pdf_catalog_file else None,
            'pdf_catalog_title': site_settings.pdf_catalog_title,
        } if hasattr(request, 'user') and request.user.is_staff else None,
    }
    
    return context

def meta_seo_context(request):
    """
    YENİ: SEO meta bilgileri için özel context processor
    Sayfa bazında dinamik meta bilgileri sağlar
    """
    # Temel meta bilgileri
    meta_data = {
        'page_type': 'website',
        'article_published_time': None,
        'article_modified_time': None,
        'article_author': None,
        'article_section': None,
        'product_price': None,
        'product_availability': None,
        'breadcrumbs': [],
    }
    
    # URL path'e göre özel meta bilgileri
    path = request.path.strip('/')
    
    if path.startswith('urunler/') and path != 'urunler/':
        # Ürün detay sayfası
        meta_data['page_type'] = 'product'
        try:
            from products.models import Product
            slug = path.split('/')[-1]
            product = Product.objects.get(slug=slug, is_active=True)
            meta_data['product_price'] = f"{product.get_price_display()}"
            meta_data['product_availability'] = 'InStock' if product.is_in_stock() else 'OutOfStock'
            meta_data['breadcrumbs'] = [
                {'name': 'Ana Sayfa', 'url': '/'},
                {'name': 'Ürünler', 'url': '/urunler/'},
                {'name': product.category.name, 'url': product.category.get_absolute_url()},
                {'name': product.name, 'url': product.get_absolute_url()},
            ]
        except:
            pass
    
    elif path.startswith('galeri/') and path != 'galeri/':
        # Galeri detay sayfası
        meta_data['page_type'] = 'article'
        try:
            from gallery.models import Gallery
            slug = path.split('/')[-1]
            gallery_item = Gallery.objects.get(slug=slug, is_active=True)
            meta_data['article_published_time'] = gallery_item.created_at.isoformat()
            meta_data['article_modified_time'] = gallery_item.updated_at.isoformat()
            meta_data['article_section'] = 'Galeri'
            meta_data['breadcrumbs'] = [
                {'name': 'Ana Sayfa', 'url': '/'},
                {'name': 'Galeri', 'url': '/galeri/'},
                {'name': gallery_item.title, 'url': gallery_item.get_absolute_url()},
            ]
        except:
            pass
    
    elif path.startswith('hakkimizda'):
        # Hakkımızda sayfası
        meta_data['page_type'] = 'article'
        meta_data['article_section'] = 'Hakkımızda'
        meta_data['breadcrumbs'] = [
            {'name': 'Ana Sayfa', 'url': '/'},
            {'name': 'Hakkımızda', 'url': '/hakkimizda/'},
        ]
    
    return {
        'meta_data': meta_data,
        'current_url': request.build_absolute_uri(),
        'canonical_url': request.build_absolute_uri(request.path),
    }

def storage_info(request):
    """
    Cloudinary storage bilgilerini sadece dashboard sayfalarına ekler
    YENİ EKLENEN CONTEXT PROCESSOR
    """
    if request.path.startswith('/dashboard/'):
        # Cache'den storage bilgilerini al (5 dakika cache)
        storage_data = cache.get('cloudinary_storage_info')
        
        if storage_data is None:
            try:
                storage_data = check_cloudinary_storage()
                cache.set('cloudinary_storage_info', storage_data, 60 * 5)  # 5 dakika cache
            except Exception as e:
                logger.error(f"Storage info error: {e}")
                storage_data = {
                    'used_gb': 0,
                    'limit_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
                    'remaining_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
                    'usage_percentage': 0,
                    'warning_level': 'success',
                    'is_warning': False,
                    'is_critical': False,
                    'error': True
                }
        
        return {
            'cloudinary_storage': storage_data,
            'storage_package_info': {
                'current_package_gb': settings.CLOUDINARY_STORAGE_LIMIT_GB,
                'available_packages': list(settings.CLOUDINARY_STORAGE_PACKAGES.keys()),
                'is_upgradeable': settings.CLOUDINARY_STORAGE_LIMIT_GB < max(settings.CLOUDINARY_STORAGE_PACKAGES.keys()),
            }
        }
    return {}

def clear_site_settings_cache():
    """Site ayarları cache'ini temizle"""
    cache.delete('site_settings')

def clear_about_cache():
    """About bilgileri cache'ini temizle"""
    cache.delete('about_info')

def clear_storage_cache():
    """Storage bilgileri cache'ini temizle - YENİ EKLENEN"""
    cache.delete('cloudinary_storage_info')

def clear_all_cache():
    """Tüm cache'i temizle"""
    clear_site_settings_cache()
    clear_about_cache()
    clear_storage_cache()  # YENİ EKLENEN

# Language context (mevcut)
def language_context(request):
    """Ana dil ayarları için context"""
    return {
        'main_language': request.COOKIES.get('main_language', settings.LANGUAGE_CODE),
        'dashboard_language': request.COOKIES.get('dashboard_language', settings.LANGUAGE_CODE),
        'main_language_choices': settings.LANGUAGES,
        'dashboard_language_choices': getattr(settings, 'DASHBOARD_LANGUAGES', settings.LANGUAGES),
    }

def get_site_enabled_languages():
    """Site için aktif dilleri getir"""
    try:
        from dashboard.models import DashboardTranslationSettings
        
        admin_settings = DashboardTranslationSettings.objects.filter(
            user__is_staff=True
        ).order_by('-updated_at').first()
        
        if admin_settings and admin_settings.enabled_languages:
            return admin_settings.enabled_languages
        else:
            return ['tr', 'en']  # Default olarak tr ve en dönder
            
    except Exception as e:
        return ['tr', 'en']  # Hata durumunda tr ve en dönder
    
    


def breadcrumb_context(request):
    """
    Dinamik breadcrumb oluşturan context processor
    URL pattern'ine göre otomatik breadcrumb yapısı
    """
    from django.urls import resolve, Resolver404
    from django.utils.translation import gettext as _
    import re
    
    try:
        # URL resolve et
        resolved = resolve(request.path)
        breadcrumbs = []
        
        # Ana sayfa her zaman ilk
        breadcrumbs.append({
            'name': _('Ana Sayfa'),
            'url': '/',
            'is_current': request.path == '/'
        })
        
        # URL path'ini analiz et
        path_parts = [part for part in request.path.strip('/').split('/') if part]
        
        # Dil prefix'ini kaldır
        if path_parts and path_parts[0] in ['tr', 'en', 'de', 'fr', 'es', 'ru', 'ar']:
            path_parts = path_parts[1:]
        
        if not path_parts:
            return {'breadcrumbs': breadcrumbs}
        
        # URL pattern'lerine göre breadcrumb oluştur
        current_path = ""
        
        for i, part in enumerate(path_parts):
            current_path += f"/{part}"
            is_last = (i == len(path_parts) - 1)
            
            # Her seviye için breadcrumb ekle
            breadcrumb = {
                'name': _get_breadcrumb_name(part, resolved.url_name, request),
                'url': current_path + "/",
                'is_current': is_last
            }
            
            # Özel durumlar için URL düzeltmesi
            if part == 'urunler':
                breadcrumb['url'] = '/urunler/'
            elif part == 'galeri':
                breadcrumb['url'] = '/galeri/'
            elif part == 'hakkimizda':
                breadcrumb['url'] = '/hakkimizda/'
            elif part == 'iletisim':
                breadcrumb['url'] = '/iletisim/'
            
            breadcrumbs.append(breadcrumb)
        
        # Detay sayfalar için özel işlem
        if resolved.url_name in ['product_detail', 'gallery_detail', 'service_detail', 'team_detail']:
            _enhance_detail_breadcrumbs(breadcrumbs, resolved, request)
        
        return {'breadcrumbs': breadcrumbs}
        
    except (Resolver404, Exception) as e:
        # Hata durumunda basit breadcrumb
        return {
            'breadcrumbs': [
                {
                    'name': _('Ana Sayfa'),
                    'url': '/',
                    'is_current': False
                },
                {
                    'name': _('Sayfa'),
                    'url': request.path,
                    'is_current': True
                }
            ]
        }

def _get_breadcrumb_name(part, url_name, request):
    """Path kısmı için uygun breadcrumb ismi döndürür"""
    from django.utils.translation import gettext as _
    
    # Önceden tanımlı section'lar
    section_names = {
        'urunler': _('Ürünler'),
        'products': _('Ürünler'),
        'galeri': _('Galeri'),
        'gallery': _('Galeri'),
        'hakkimizda': _('Hakkımızda'),
        'about': _('Hakkımızda'),
        'iletisim': _('İletişim'),
        'contact': _('İletişim'),
        'hizmetler': _('Hizmetler'),
        'services': _('Hizmetler'),
        'ekip': _('Ekibimiz'),
        'team': _('Ekibimiz'),
        'kategoriler': _('Kategoriler'),
        'categories': _('Kategoriler'),
    }
    
    if part in section_names:
        return section_names[part]
    
    # Slug'dan isim çıkarmaya çalış
    if url_name in ['product_detail', 'category_detail', 'gallery_detail']:
        return _get_object_name_from_slug(part, url_name)
    
    # Varsayılan: ilk harfi büyük, tire ve alt çizgiyi boşlukla değiştir
    return part.replace('-', ' ').replace('_', ' ').title()

def _get_object_name_from_slug(slug, url_name):
    """Slug'dan object ismini getirir"""
    try:
        if url_name == 'product_detail':
            from products.models import Product
            obj = Product.objects.get(slug=slug, is_active=True)
            return obj.name
        elif url_name == 'category_detail':
            from products.models import Category
            obj = Category.objects.get(slug=slug, is_active=True)
            return obj.name
        elif url_name == 'gallery_detail':
            from gallery.models import Gallery
            obj = Gallery.objects.get(slug=slug, is_active=True)
            return obj.title
        elif url_name == 'service_detail':
            from about.models import Service
            obj = Service.objects.get(slug=slug, is_active=True)
            return obj.title
        elif url_name == 'team_detail':
            from about.models import TeamMember
            obj = TeamMember.objects.get(slug=slug, is_active=True)
            return obj.name
    except:
        pass
    
    # Hata durumunda slug'ı temizle
    return slug.replace('-', ' ').title()

def _enhance_detail_breadcrumbs(breadcrumbs, resolved, request):
    """Detay sayfaları için breadcrumb'ları zenginleştir"""
    try:
        if resolved.url_name == 'product_detail':
            # Ürün detay için kategori bilgisi ekle
            from products.models import Product
            slug = resolved.kwargs.get('slug')
            if slug:
                product = Product.objects.select_related('category').get(slug=slug, is_active=True)
                
                # Kategori breadcrumb'ı ekle (sondan bir önceki pozisyona)
                if len(breadcrumbs) >= 2:
                    category_breadcrumb = {
                        'name': product.category.name,
                        'url': product.category.get_absolute_url(),
                        'is_current': False
                    }
                    breadcrumbs.insert(-1, category_breadcrumb)
                    
                # Son breadcrumb'ı güncelle
                breadcrumbs[-1]['name'] = product.name
        
    except Exception as e:
        # Hata durumunda mevcut breadcrumb'ları koru
        pass

def get_structured_breadcrumbs(request):
    """
    JSON-LD structured data için breadcrumb verisi
    """
    breadcrumb_data = breadcrumb_context(request)
    breadcrumbs = breadcrumb_data.get('breadcrumbs', [])
    
    if len(breadcrumbs) <= 1:
        return None
    
    structured_breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for i, breadcrumb in enumerate(breadcrumbs):
        if not breadcrumb.get('is_current', False):  # Son öğeyi dahil etme
            structured_breadcrumbs["itemListElement"].append({
                "@type": "ListItem",
                "position": i + 1,
                "name": breadcrumb['name'],
                "item": f"{request.scheme}://{request.get_host()}{breadcrumb['url']}"
            })
    
    return structured_breadcrumbs






def footer_context(request):
    """
    Footer için gerekli context verilerini sağlar
    """
    try:
        from about.models import Service
        from core.models import LegalPage
        
        # Footer'da gösterilecek hizmetler (maksimum 6)
        footer_services = Service.objects.filter(
            is_active=True, 
            is_footer=True
        ).order_by('order')[:6]
        
        # Yasal sayfalar
        legal_pages = {}
        for page in LegalPage.objects.filter(is_active=True):
            legal_pages[page.page_type] = {
                'title': page.title,
                'url': page.get_absolute_url(),
                'slug': page.slug
            }
        
        return {
            'footer_services': footer_services,
            'legal_pages': legal_pages,
            'has_legal_pages': bool(legal_pages),
        }
    except:
        # Model yoksa boş döner
        return {
            'footer_services': [],
            'legal_pages': {},
            'has_legal_pages': False,
        }