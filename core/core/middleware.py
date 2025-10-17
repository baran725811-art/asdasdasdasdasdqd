# core/middleware.py
import logging
from django.http import HttpResponseForbidden, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import re
import time
from django.utils import translation
from django.core.cache import cache
from django.conf import settings
import logging

# Security logger
security_logger = logging.getLogger('core.security')

class SecurityHeadersMiddleware:
    """
    Gelişmiş güvenlik başlıkları middleware'i
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Güvenlik başlıklarını ekle
        self._add_security_headers(response)
        
        # CSP başlığını ekle
        self._add_csp_header(response)
        
        return response
    
    def _add_security_headers(self, response):
        """Temel güvenlik başlıkları"""
        # XSS koruması
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content type sniffing koruması
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Clickjacking koruması
        response['X-Frame-Options'] = 'DENY'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy (önceki Feature-Policy)
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=(), '
            'accelerometer=(), ambient-light-sensor=()'
        )
        
        # HSTS (sadece HTTPS'de)
        if hasattr(settings, 'SECURE_HSTS_SECONDS') and settings.SECURE_HSTS_SECONDS > 0:
            hsts_header = f'max-age={settings.SECURE_HSTS_SECONDS}'
            if getattr(settings, 'SECURE_HSTS_INCLUDE_SUBDOMAINS', False):
                hsts_header += '; includeSubDomains'
            if getattr(settings, 'SECURE_HSTS_PRELOAD', False):
                hsts_header += '; preload'
            response['Strict-Transport-Security'] = hsts_header
    
    def _add_csp_header(self, response):
        """Content Security Policy başlığı"""
        csp_directives = []
        
        # CSP direktiflerini settings'ten al
        csp_settings = {
            'default-src': getattr(settings, 'CSP_DEFAULT_SRC', ["'self'"]),
            'script-src': getattr(settings, 'CSP_SCRIPT_SRC', ["'self'"]),
            'style-src': getattr(settings, 'CSP_STYLE_SRC', ["'self'"]),
            'img-src': getattr(settings, 'CSP_IMG_SRC', ["'self'"]),
            'font-src': getattr(settings, 'CSP_FONT_SRC', ["'self'"]),
            'connect-src': getattr(settings, 'CSP_CONNECT_SRC', ["'self'"]),
            'frame-src': getattr(settings, 'CSP_FRAME_SRC', ["'none'"]),
            'object-src': getattr(settings, 'CSP_OBJECT_SRC', ["'none'"]),
            'media-src': getattr(settings, 'CSP_MEDIA_SRC', ["'self'"]),
        }
        
        for directive, sources in csp_settings.items():
            if sources:
                csp_directives.append(f"{directive} {' '.join(sources)}")
        
        if csp_directives:
            response['Content-Security-Policy'] = '; '.join(csp_directives)

class SecurityMonitoringMiddleware:
    """
    Güvenlik izleme middleware'i - şüpheli aktiviteleri loglar
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Şüpheli pattern'ler
        self.suspicious_patterns = [
            r'\.\./',  # Directory traversal
            r'<script',  # XSS attempt
            r'javascript:',  # XSS attempt
            r'union\s+select',  # SQL injection
            r'drop\s+table',  # SQL injection
            r'exec\s*\(',  # Code injection
            r'eval\s*\(',  # Code injection
        ]

    def __call__(self, request):
        # İstek öncesi kontroller
        self._check_suspicious_request(request)
        self._check_rate_limit(request)
        
        response = self.get_response(request)
        
        # Response sonrası loglar
        self._log_response(request, response)
        
        return response
    
    def _check_suspicious_request(self, request):
        """Şüpheli istek kontrolü"""
        ip_address = self._get_client_ip(request)
        
        # Query string ve POST data kontrolü
        all_params = []
        all_params.extend(request.GET.values())
        if hasattr(request, 'POST'):
            all_params.extend(request.POST.values())
        
        for param in all_params:
            for pattern in self.suspicious_patterns:
                if re.search(pattern, str(param), re.I):
                    security_logger.warning(
                        f'Suspicious request pattern detected: {pattern} '
                        f'from IP {ip_address} on URL {request.path}'
                    )
                    # Opsiyonel: IP'yi geçici olarak engelle
                    self._block_suspicious_ip(ip_address)
                    break
    
    def _check_rate_limit(self, request):
        """Basit rate limiting"""
        ip_address = self._get_client_ip(request)
        cache_key = f'rate_limit_{ip_address}'
        
        # Son 1 dakikadaki istek sayısını kontrol et
        requests = cache.get(cache_key, [])
        now = time.time()
        
        # 1 dakikadan eski istekleri temizle
        requests = [req_time for req_time in requests if now - req_time < 60]
        
        # Yeni isteği ekle
        requests.append(now)
        
        # Cache'e kaydet
        cache.set(cache_key, requests, 60)
        
        # Limit kontrolü (dakikada 100 istek)
        if len(requests) > 100:
            security_logger.warning(
                f'Rate limit exceeded for IP {ip_address}: {len(requests)} requests/minute'
            )
    
    def _block_suspicious_ip(self, ip_address):
        """Şüpheli IP'yi geçici olarak engelle"""
        if getattr(settings, 'SECURITY_MONITORING', {}).get('BLOCK_SUSPICIOUS_IPS', False):
            cache_key = f'blocked_ip_{ip_address}'
            cache.set(cache_key, True, 300)  # 5 dakika engelle
    
    def _get_client_ip(self, request):
        """Gerçek client IP'sini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
    
    def _log_response(self, request, response):
        """Response logları"""
        if response.status_code >= 400:
            ip_address = self._get_client_ip(request)
            security_logger.info(
                f'HTTP {response.status_code} response for {request.method} '
                f'{request.path} from IP {ip_address}'
            )

class LoginSecurityMiddleware:
    """
    Login güvenliği middleware'i
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Login sayfası kontrolü
        if request.path.startswith('/dashboard/login/') and request.method == 'POST':
            self._check_login_attempts(request)
        
        response = self.get_response(request)
        return response
    
    def _check_login_attempts(self, request):
        """Başarısız login denemelerini kontrol et"""
        ip_address = self._get_client_ip(request)
        cache_key = f'login_attempts_{ip_address}'
        
        attempts = cache.get(cache_key, 0)
        max_attempts = getattr(settings, 'SECURITY_MONITORING', {}).get('MAX_LOGIN_ATTEMPTS', 5)
        
        if attempts >= max_attempts:
            security_logger.warning(
                f'Login attempts exceeded for IP {ip_address}: {attempts} attempts'
            )
            # IP'yi geçici olarak engelle
            block_key = f'blocked_login_{ip_address}'
            timeout = getattr(settings, 'SECURITY_MONITORING', {}).get('LOGIN_ATTEMPT_TIMEOUT', 300)
            cache.set(block_key, True, timeout)
    
    def _get_client_ip(self, request):
        """Gerçek client IP'sini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

# Login failed signal handler
@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Başarısız login denemelerini logla"""
    ip_address = request.META.get('REMOTE_ADDR', '')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    
    username = credentials.get('username', 'Unknown')
    
    security_logger.warning(
        f'Failed login attempt: username={username}, IP={ip_address}'
    )
    
    # Başarısız deneme sayısını artır
    cache_key = f'login_attempts_{ip_address}'
    attempts = cache.get(cache_key, 0)
    cache.set(cache_key, attempts + 1, 300)  # 5 dakika

# MEVCUT MIDDLEWARE'LER (SecurityMiddleware, IPAddressMiddleware, etc.) AYNI KALIR
class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # SQL injection koruması
        if self._check_sql_injection(request):
            return HttpResponseForbidden("Forbidden")
            
        # XSS koruması
        if self._check_xss(request):
            return HttpResponseForbidden("Forbidden")
            
        response = self.get_response(request)
        
        # Güvenlik başlıkları
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response
        
    def _check_sql_injection(self, request):
        sql_patterns = [
            r'(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)(\s|$)',
            r'--',
            r';',
            r'\/\*.*\*\/',
        ]
        
        for param in request.GET.values():
            for pattern in sql_patterns:
                if re.search(pattern, param, re.I):
                    return True
        return False
        
    def _check_xss(self, request):
        xss_patterns = [
            r'<script.*?>.*?<\/script>',
            r'javascript:',
            r'onerror=',
            r'onload=',
        ]
        
        for param in request.GET.values():
            for pattern in xss_patterns:
                if re.search(pattern, param, re.I):
                    return True
        return False

class IPAddressMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            request.ip_address = x_forwarded_for.split(',')[0]
        else:
            request.ip_address = request.META.get('REMOTE_ADDR')
            
        response = self.get_response(request)
        return response

class SEOCanonicalMiddleware:
    """
    SEO için Canonical URL ve yönlendirme middleware'i
    - www/non-www standardizasyonu
    - Trailing slash kontrolü
    - Duplicate URL önleme
    - 301 redirectler
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin, dashboard ve API URL'lerini atla
        skip_paths = ['/admin/', '/dashboard/', '/api/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # WWW/non-WWW standardizasyonu
        redirect_response = self._check_www_redirect(request)
        if redirect_response:
            return redirect_response
        
        # Trailing slash kontrolü
        redirect_response = self._check_trailing_slash(request)
        if redirect_response:
            return redirect_response
            
        # HTTP/HTTPS kontrolü (production için)
        redirect_response = self._check_https_redirect(request)
        if redirect_response:
            return redirect_response
        
        response = self.get_response(request)
        
        # Canonical URL header'ı ekle
        self._add_canonical_header(request, response)
        
        return response
    
    def _check_www_redirect(self, request):
        """WWW'dan non-WWW'ya yönlendirme (isteğe bağlı)"""
        host = request.get_host().lower()
        
        # www'dan non-www'ya yönlendir (SEO için tek domain)
        if host.startswith('www.'):
            new_host = host[4:]  # www. kısmını kaldır
            new_url = f"{request.scheme}://{new_host}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(new_url)
        
        return None
    
    def _check_trailing_slash(self, request):
        """Trailing slash standardizasyonu"""
        path = request.path_info
        
        # Dosya uzantılı URL'leri atla (.css, .js, .png vb.)
        if '.' in path.split('/')[-1]:
            return None
        
        # Django'nun APPEND_SLASH ayarına göre davran
        if getattr(settings, 'APPEND_SLASH', True):
            if not path.endswith('/') and path != '/':
                new_url = f"{path}/{request.META.get('QUERY_STRING', '')}"
                if request.META.get('QUERY_STRING'):
                    new_url = f"{path}/?{request.META.get('QUERY_STRING')}"
                return HttpResponsePermanentRedirect(new_url)
        
        return None
    
    def _check_https_redirect(self, request):
        """HTTPS yönlendirmesi (production için)"""
        if getattr(settings, 'SECURE_SSL_REDIRECT', False):
            if not request.is_secure():
                new_url = f"https://{request.get_host()}{request.get_full_path()}"
                return HttpResponsePermanentRedirect(new_url)
        
        return None
    
    def _add_canonical_header(self, request, response):
        """Response'a canonical URL header'ı ekle"""
        if hasattr(response, 'status_code') and response.status_code == 200:
            canonical_url = f"{request.scheme}://{request.get_host()}{request.path}"
            response['Link'] = f'<{canonical_url}>; rel="canonical"'

class URLRedirectMiddleware:
    """
    Eski URL'leri yeni URL'lere yönlendirme middleware'i
    301 redirectler ile SEO juice'ini korur
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URL yönlendirme kuralları - İhtiyaca göre güncellenebilir
        self.redirects = {
            # Eski format -> Yeni format
            '/products/': '/urunler/',
            '/gallery/': '/galeri/',
            '/about/': '/hakkimizda/',
            '/contact/': '/iletisim/',
            
            # Eski slug'lar -> Yeni slug'lar (örnekler)
            # '/old-product-name/': '/urunler/new-product-name/',
        }

    def __call__(self, request):
        # Admin ve dashboard URL'lerini atla
        if request.path.startswith('/admin/') or request.path.startswith('/dashboard/'):
            return self.get_response(request)
        
        # URL yönlendirme kontrolü
        redirect_response = self._check_redirects(request)
        if redirect_response:
            return redirect_response
        
        return self.get_response(request)
    
    def _check_redirects(self, request):
        """Tanımlı yönlendirmeleri kontrol et"""
        current_path = request.path
        
        # Tam URL eşleşmesi
        if current_path in self.redirects:
            new_path = self.redirects[current_path]
            if request.META.get('QUERY_STRING'):
                new_path = f"{new_path}?{request.META.get('QUERY_STRING')}"
            return HttpResponsePermanentRedirect(new_path)
        
        # Pattern tabanlı yönlendirmeler (ihtiyaç halinde)
        return None

class DashboardLocaleMiddleware:
    """Dashboard dil middleware'i - Bağımsız çalışır"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Dashboard URL pattern kontrolü
        is_dashboard = (
            request.path.startswith('/dashboard/') or 
            '/dashboard/' in request.path or
            request.path_info.startswith('/dashboard/')
        )
        
        if is_dashboard and request.user.is_authenticated:
            dashboard_language = 'tr'  # Varsayılan
            
            try:
                from dashboard.models import DashboardTranslationSettings
                user_settings = DashboardTranslationSettings.objects.get(user=request.user)
                
                # Dashboard dili (primary_language'den BAĞIMSIZ)
                dashboard_language = user_settings.dashboard_language
                print(f"[MIDDLEWARE] Kullanıcı {request.user.username} dashboard dili: {dashboard_language}")
                
            except DashboardTranslationSettings.DoesNotExist:
                dashboard_language = request.COOKIES.get('dashboard_language', 'tr')
                print(f"[MIDDLEWARE] Cookie'den dashboard dili: {dashboard_language}")
            except Exception as e:
                print(f"[MIDDLEWARE] Hata: {e}")
                dashboard_language = 'tr'
            
            # Dil aktivasyonu
            from django.utils import translation
            if dashboard_language in [lang[0] for lang in settings.LANGUAGES]:
                translation.activate(dashboard_language)
                request.LANGUAGE_CODE = dashboard_language
                print(f"[MIDDLEWARE] Dashboard dili aktive edildi: {dashboard_language}")
            
        response = self.get_response(request)
        
        # Dashboard response'unda cookie ayarla
        if is_dashboard and hasattr(request, 'LANGUAGE_CODE'):
            response.set_cookie(
                'dashboard_language', 
                request.LANGUAGE_CODE,
                max_age=365*24*60*60,
                path='/dashboard/',
                secure=False
            )
        
        return response

class ForceLanguageMiddleware:
    """
    Browser'ın dil tercihini kontrol eder, ancak Django'nun i18n sistemini bozmaz
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Dashboard URL'leri için özel işlem yapma
        if request.path.startswith('/dashboard/'):
            response = self.get_response(request)
            return response
        
        # Eğer URL'de dil prefix'i yoksa ve root URL değilse, redirect etme
        # Django'nun LocaleMiddleware'inin normal çalışmasına izin ver
        
        response = self.get_response(request)
        return response
    
class SitePrimaryLanguageMiddleware:
    """
    Site ana dil yönlendirmesi - kullanıcının ana diline göre
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Dashboard URL'leri için işlem yapma
        if request.path.startswith('/dashboard/'):
            response = self.get_response(request)
            return response
        
        # Root URL kontrolü - SADECE authenticated user ve TAM ROOT URL
        if (request.path == '/' and 
            request.user.is_authenticated and 
            not request.path.startswith('/tr/') and  # Zaten TR'de değilse
            not hasattr(request, '_redirect_processed')):  # İlk kez işleniyor
            
            try:
                from dashboard.models import DashboardTranslationSettings
                user_settings = DashboardTranslationSettings.objects.get(user=request.user)
                primary_language = user_settings.primary_language
                
                # Sadece farklı dildeyse yönlendir
                if primary_language != 'tr':
                    from django.shortcuts import redirect
                    request._redirect_processed = True
                    print(f"[SITE MIDDLEWARE] Root URL, ana dile yönlendiriliyor: /{primary_language}/")
                    return redirect(f'/{primary_language}/')
                    
            except DashboardTranslationSettings.DoesNotExist:
                pass
            except Exception as e:
                print(f"[SITE MIDDLEWARE] Hata: {e}")
        
        response = self.get_response(request)
        return response
# Error tracking logger
error_logger = logging.getLogger('django')

class Error404TrackingMiddleware:
    """
    404 hatalarını izleyen ve SEO için optimize eden middleware
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # 404 hatalarını izle
        if response.status_code == 404:
            self._track_404_error(request)
        
        return response
    
    def _track_404_error(self, request):
        """404 hatalarını logla ve cache'e kaydet"""
        if not getattr(settings, 'TRACK_404_ERRORS', True):
            return
        
        ip_address = self._get_client_ip(request)
        path = request.path
        referrer = request.META.get('HTTP_REFERER', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Rate limiting - aynı IP'den çok fazla 404 loglanmasın
        cache_key = f'404_rate_limit_{ip_address}'
        error_count = cache.get(cache_key, 0)
        max_errors = getattr(settings, 'MAX_404_LOGS_PER_IP', 10)
        
        if error_count >= max_errors:
            return
        
        # Error tracking cache'e ekle
        cache.set(cache_key, error_count + 1, 3600)  # 1 saat
        
        # 404 hatalarını toplu şekilde cache'e kaydet
        errors_cache_key = '404_errors_list'
        errors = cache.get(errors_cache_key, [])
        
        error_data = {
            'path': path,
            'ip': ip_address,
            'referrer': referrer,
            'user_agent': user_agent[:200],  # Limit user agent length
            'timestamp': timezone.now().isoformat(),
        }
        
        errors.append(error_data)
        
        # Son 100 hatayı sakla
        if len(errors) > 100:
            errors = errors[-100:]
        
        cache.set(errors_cache_key, errors, 86400)  # 24 saat
        
        # Log kritik 404'leri
        if self._is_critical_404(path):
            error_logger.warning(
                f'Critical 404: {path} | IP: {ip_address} | Referrer: {referrer}'
            )
    
    def _is_critical_404(self, path):
        """Kritik 404 hatalarını belirle"""
        critical_patterns = [
            '/sitemap.xml',
            '/robots.txt',
            '/favicon.ico',
            '.xml',
            '.json',
        ]
        
        # Admin, dashboard, static dosyalar kritik değil
        skip_patterns = [
            '/admin/',
            '/dashboard/',
            '/static/',
            '/media/',
            '.css',
            '.js',
            '.ico',
            '.png',
            '.jpg',
            '.jpeg',
            '.gif',
        ]
        
        for pattern in skip_patterns:
            if pattern in path:
                return False
        
        for pattern in critical_patterns:
            if pattern in path:
                return True
        
        # Çok sayıda / içeren path'ler (broken deep links)
        if path.count('/') > 3:
            return True
        
        return False
    
    def _get_client_ip(self, request):
        """Gerçek client IP'sini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

class MaintenanceModeMiddleware:
    """
    Bakım modu middleware'i
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bakım modu kontrolü
        maintenance_settings = getattr(settings, 'MAINTENANCE_MODE_SETTINGS', {})
        
        if maintenance_settings.get('ENABLED', False):
            # İzinli IP'leri kontrol et
            allowed_ips = maintenance_settings.get('ALLOWED_IPS', [])
            client_ip = self._get_client_ip(request)
            
            if client_ip not in allowed_ips:
                # Admin ve dashboard'a erişimi engelleme
                if not request.path.startswith('/admin/') and not request.path.startswith('/dashboard/'):
                    from core.views import maintenance_view
                    return maintenance_view(request)
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        """Gerçek client IP'sini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')