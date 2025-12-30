import json
import logging
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden
from django.template import TemplateDoesNotExist
from django.utils.translation import activate, gettext as _
from django.utils import timezone
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import requires_csrf_token
from contact.forms import ContactForm
from reviews.forms import ReviewForm
from reviews.models import Review
from core.models import LegalPage, CookieConsent

from products.models import Product
from gallery.models import Gallery

def contact(request):
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        if 'form_type' in request.POST:
            if request.POST['form_type'] == 'contact':
                contact_form = ContactForm(request.POST)
                review_form = ReviewForm()
                if contact_form.is_valid():
                    contact_form.save()
                    messages.success(request, 'Mesajınız başarıyla gönderildi.')
                    return redirect('contact:contact')
            
            elif request.POST['form_type'] == 'review' and request.user.is_authenticated:
                review_form = ReviewForm(request.POST)
                contact_form = ContactForm()
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user = request.user
                    review.save()
                    messages.success(request, 'Değerlendirmeniz başarıyla kaydedildi.')
                    return redirect('contact:contact')
    else:
        contact_form = ContactForm()
        review_form = ReviewForm()

    context = {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': reviews,
    }
    return render(request, 'contact/contact.html', context)


def ratelimit_view(request, exception):
    return render(request, 'errors/ratelimit.html', {'message': 'Çok fazla istek gönderildi. Lütfen birkaç dakika bekleyip tekrar deneyin.'}, status=429)


# core/views.py - YENI EKLENECEK KOD


@require_POST
def set_main_language(request):
    """Ana dil ayarlama - admin ve dashboard için"""
    try:
        data = json.loads(request.body)
        language_code = data.get('language')
        
        # Dil kodu geçerlilik kontrolü
        available_languages = [lang[0] for lang in settings.LANGUAGES]
        if language_code not in available_languages:
            return JsonResponse({
                'success': False, 
                'error': 'Geçersiz dil kodu'
            }, status=400)
        
        # Response oluştur
        response = JsonResponse({
            'success': True,
            'language': language_code,
            'message': f'Ana dil {language_code} olarak ayarlandı'
        })
        
        # Ana dil cookie'sini ayarla (1 yıl)
        response.set_cookie(
            'main_language',
            language_code,
            max_age=365 * 24 * 60 * 60,  # 1 yıl
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=False,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE
        )
        
        # Django'nun varsayılan dil cookie'sini de ayarla
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE
        )
        
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Geçersiz JSON verisi'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@staff_member_required(login_url='/admin/login/')
@require_POST
def set_dashboard_language(request):
    """Dashboard arayüz dili ayarlama (geçici)"""
    try:
        data = json.loads(request.body)
        language_code = data.get('language')
        
        # Dashboard dilleri kontrolü
        dashboard_languages = getattr(settings, 'DASHBOARD_LANGUAGES', settings.LANGUAGES)
        available_languages = [lang[0] for lang in dashboard_languages]
        
        if language_code not in available_languages:
            return JsonResponse({
                'success': False,
                'error': 'Geçersiz dashboard dil kodu'
            }, status=400)
        
        response = JsonResponse({
            'success': True,
            'language': language_code,
            'message': f'Dashboard dili geçici olarak {language_code} yapıldı'
        })
        
        # Dashboard dil cookie'si (session bazlı - tarayıcı kapanınca siler)
        response.set_cookie(
            'dashboard_language',
            language_code,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=False,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE
        )
        
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Geçersiz JSON verisi'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def get_language_info(request):
    """Dil bilgilerini JSON olarak döndür"""
    return JsonResponse({
        'main_language': request.COOKIES.get('main_language', settings.LANGUAGE_CODE),
        'dashboard_language': request.COOKIES.get('dashboard_language', settings.LANGUAGE_CODE),
        'current_language': request.LANGUAGE_CODE,
        'available_languages': [
            {'code': lang[0], 'name': lang[1]} 
            for lang in settings.LANGUAGES
        ],
        'dashboard_languages': [
            {'code': lang[0], 'name': str(lang[1])} 
            for lang in getattr(settings, 'DASHBOARD_LANGUAGES', settings.LANGUAGES)
        ]
    })
    
    


logger = logging.getLogger(__name__)

def custom_404_view(request, exception=None):
    """
    SEO-friendly 404 hata sayfası
    - Arama önerileri
    - Popüler içerikler
    - Breadcrumb navigation
    - Structured data
    """
    # Logging
    logger.warning(f'404 Error: {request.path} from IP {request.META.get("REMOTE_ADDR", "")}')
    
    # Arama önerileri için içerik - güvenli try/except blokları
    popular_products = []
    recent_gallery = []
    search_suggestions = []
    
    try:
        # Popüler ürünler - sadece model varsa
        if Product:
            popular_products = Product.objects.filter(
                is_active=True
            ).order_by('-created_at')[:6]
        
        # Son galeri öğeleri - sadece model varsa
        if Gallery:
            recent_gallery = Gallery.objects.filter(
                is_active=True
            ).order_by('-created_at')[:4]
        
        # Önerilen aramalar (path'den kelime çıkar)
        path_words = request.path.strip('/').replace('-', ' ').split('/')
        
        for word in path_words:
            if len(word) > 2 and Product:  # 2 karakterden uzun kelimeler
                # Ürünlerde ara
                products = Product.objects.filter(
                    name__icontains=word,
                    is_active=True
                )[:3]
                if products:
                    search_suggestions.extend([
                        {
                            'type': 'product',
                            'title': product.name,
                            'url': product.get_absolute_url(),
                            'description': product.description[:100] if product.description else ''
                        } for product in products
                    ])
        
        # Eğer hiç öneri yoksa, rastgele popüler içerik göster
        if not search_suggestions and popular_products:
            search_suggestions = [
                {
                    'type': 'product',
                    'title': product.name,
                    'url': product.get_absolute_url(),
                    'description': product.description[:100] if product.description else ''
                } for product in random.sample(list(popular_products), min(3, len(popular_products)))
            ]
    
    except Exception as e:
        logger.error(f'Error generating 404 suggestions: {e}')
        popular_products = []
        recent_gallery = []
        search_suggestions = []
    
    context = {
        'error_code': '404',
        'error_title': _('Sayfa Bulunamadı'),
        'error_message': _('Aradığınız sayfa bulunamadı veya taşınmış olabilir.'),
        'requested_path': request.path,
        'popular_products': popular_products,
        'recent_gallery': recent_gallery,
        'search_suggestions': search_suggestions,
        'show_search': True,
        'canonical_url': request.build_absolute_uri(),
        'meta_description': _('Aradığınız sayfa bulunamadı. Popüler ürünlerimizi ve içeriklerimizi keşfedin.'),
        'structured_data': {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': _('404 - Sayfa Bulunamadı'),
            'description': _('Aradığınız sayfa bulunamadı'),
            'url': request.build_absolute_uri(),
            'mainEntity': {
                '@type': 'Thing',
                'name': _('Sayfa Bulunamadı'),
                'description': _('İstenen kaynak bulunamadı')
            }
        }
    }
    
    return render(request, 'errors/404.html', context, status=404)

def custom_500_view(request):
    """
    SEO-friendly 500 hata sayfası
    - Teknik destek bilgileri
    - Alternatif sayfalar
    - Sistem durumu
    """
    # Hata logging
    logger.error(f'500 Error on {request.path} from IP {request.META.get("REMOTE_ADDR", "")}')
    
    # Güvenli içerik yükleme
    try:
        # Temel sayfa linkleri
        safe_links = [
            {'title': _('Ana Sayfa'), 'url': '/'},
            {'title': _('Ürünler'), 'url': '/urunler/'},
            {'title': _('Galeri'), 'url': '/galeri/'},
            {'title': _('Hakkımızda'), 'url': '/hakkimizda/'},
            {'title': _('İletişim'), 'url': '/iletisim/'},
        ]
    except:
        safe_links = []
    
    context = {
        'error_code': '500',
        'error_title': _('Sunucu Hatası'),
        'error_message': _('Geçici bir teknik sorun yaşanıyor. Lütfen birkaç dakika sonra tekrar deneyin.'),
        'safe_links': safe_links,
        'show_contact': True,
        'support_email': getattr(settings, 'CONTACT_EMAIL', 'info@example.com'),
        'canonical_url': request.build_absolute_uri(),
        'meta_description': _('Geçici sunucu hatası. Yakında normale dönecektir.'),
        'structured_data': {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': _('500 - Sunucu Hatası'),
            'description': _('Geçici sunucu hatası'),
            'url': request.build_absolute_uri()
        }
    }
    
    return render(request, 'errors/500.html', context, status=500)

def custom_403_view(request, exception=None):
    """
    SEO-friendly 403 hata sayfası
    """
    logger.warning(f'403 Error: {request.path} from IP {request.META.get("REMOTE_ADDR", "")}')
    
    context = {
        'error_code': '403',
        'error_title': _('Erişim Reddedildi'),
        'error_message': _('Bu sayfaya erişim izniniz bulunmuyor.'),
        'show_login': not request.user.is_authenticated,
        'canonical_url': request.build_absolute_uri(),
        'meta_description': _('Bu sayfaya erişim izniniz bulunmuyor.'),
        'structured_data': {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': _('403 - Erişim Reddedildi'),
            'description': _('Erişim reddedildi'),
            'url': request.build_absolute_uri()
        }
    }
    
    return render(request, 'errors/403.html', context, status=403)

def custom_400_view(request, exception=None):
    """
    400 Bad Request hata sayfası
    """
    logger.warning(f'400 Error: {request.path} from IP {request.META.get("REMOTE_ADDR", "")}')
    
    context = {
        'error_code': '400',
        'error_title': _('Hatalı İstek'),
        'error_message': _('Gönderilen istek hatalı. Lütfen sayfayı yenileyin ve tekrar deneyin.'),
        'canonical_url': request.build_absolute_uri(),
        'meta_description': _('Hatalı istek gönderildi.'),
        'structured_data': {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': _('400 - Hatalı İstek'),
            'description': _('Hatalı istek'),
            'url': request.build_absolute_uri()
        }
    }
    
    return render(request, 'errors/400.html', context, status=400)

def maintenance_view(request):
    """
    Bakım modu sayfası
    """
    context = {
        'error_code': '503',
        'error_title': _('Bakım Modu'),
        'error_message': _('Site şu anda bakım modunda. Kısa süre sonra tekrar açılacaktır.'),
        'estimated_time': _('Tahmini süre: 30 dakika'),
        'canonical_url': request.build_absolute_uri(),
        'meta_description': _('Site bakım modunda.'),
        'structured_data': {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': _('503 - Bakım Modu'),
            'description': _('Site bakım modunda'),
            'url': request.build_absolute_uri()
        }
    }
    
    return render(request, 'errors/maintenance.html', context, status=503)


@requires_csrf_token
def csrf_failure_view(request, reason=""):
    """Özel CSRF hata sayfası"""
    context = {
        'error_code': '403',
        'error_title': _('Güvenlik Hatası'),
        'error_message': _('CSRF doğrulama hatası. Lütfen sayfayı yenileyin ve tekrar deneyin.'),
        'reason': reason,
        'canonical_url': request.build_absolute_uri(),
    }
    return render(request, 'errors/csrf_failure.html', context, status=403)






def legal_page_detail(request, slug):
    """Yasal sayfa detayı"""
    page = get_object_or_404(LegalPage, slug=slug, is_active=True)
    
    context = {
        'page': page,
        'meta_title': page.meta_title,
        'meta_description': page.meta_description,
        'canonical_url': request.build_absolute_uri(),
        'breadcrumb_items': [
            {'title': 'Ana Sayfa', 'url': '/'},
            {'title': page.title, 'url': ''}
        ]
    }
    
    return render(request, 'legal/legal_page_detail.html', context)

@require_POST
def save_cookie_preferences(request):
    """Çerez tercihlerini kaydet"""
    try:
        data = json.loads(request.body)
        
        # Session key'i al
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # IP adresini al
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Çerez onayını kaydet veya güncelle
        consent, created = CookieConsent.objects.update_or_create(
            session_key=session_key,
            defaults={
                'ip_address': ip_address,
                'necessary_cookies': data.get('necessary', True),
                'functional_cookies': data.get('functional', False),
                'analytics_cookies': data.get('analytics', False),
                'marketing_cookies': data.get('marketing', False),
            }
        )
        
        response = JsonResponse({
            'success': True,
            'message': 'Çerez tercihleri kaydedildi.',
            'preferences': {
                'necessary': consent.necessary_cookies,
                'functional': consent.functional_cookies,
                'analytics': consent.analytics_cookies,
                'marketing': consent.marketing_cookies,
            }
        })
        
        # Çerez onay cookie'sini ayarla
        consent_data = {
            'necessary': consent.necessary_cookies,
            'functional': consent.functional_cookies,
            'analytics': consent.analytics_cookies,
            'marketing': consent.marketing_cookies,
        }
        
        response.set_cookie(
            'cookie_consent',
            json.dumps(consent_data),
            max_age=365 * 24 * 60 * 60,  # 1 yıl
            secure=not settings.DEBUG,
            httponly=False,  # JavaScript erişimi için
            samesite='Strict'
        )
        
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Geçersiz JSON verisi'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def get_cookie_preferences(request):
    """Mevcut çerez tercihlerini getir"""
    try:
        session_key = request.session.session_key
        
        if session_key:
            consent = CookieConsent.objects.filter(session_key=session_key).first()
            if consent:
                return JsonResponse({
                    'success': True,
                    'preferences': {
                        'necessary': consent.necessary_cookies,
                        'functional': consent.functional_cookies,
                        'analytics': consent.analytics_cookies,
                        'marketing': consent.marketing_cookies,
                    },
                    'consent_date': consent.consent_date.isoformat()
                })
        
        # Varsayılan tercihler
        return JsonResponse({
            'success': True,
            'preferences': {
                'necessary': True,
                'functional': False,
                'analytics': False,
                'marketing': False,
            },
            'consent_date': None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)