#core\core\urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from . import views
from dashboard.views import catalog_view
from django.views.i18n import JavaScriptCatalog


# Sitemap'leri güvenli import
try:
    from .sitemaps import (
        StaticViewSitemap, ProductSitemap, CategorySitemap, 
        GallerySitemap, ServiceSitemap, TeamSitemap, CarouselSitemap
    )
    sitemaps = {
        'static': StaticViewSitemap,
        'products': ProductSitemap,
        'categories': CategorySitemap,
        'gallery': GallerySitemap,
        'services': ServiceSitemap,
        'team': TeamSitemap,
        'carousel': CarouselSitemap,
    }
except ImportError:
    sitemaps = {}

# Dil-bağımsız URL'ler (admin, sitemap, dil değiştirme, API'ler)
urlpatterns = [
    path(getattr(settings, 'ADMIN_URL', 'admin/'), admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('captcha/', include('captcha.urls')),
    path('set_language/', set_language, name='set_language'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    
    # DASHBOARD - dil-bağımsız
    path('dashboard/', include('dashboard.urls')),
    
    # Ana dil yönetimi API'leri
    path('api/set-main-language/', views.set_main_language, name='set_main_language'),
    path('api/set-dashboard-language/', views.set_dashboard_language, name='set_dashboard_language'),
    path('api/language-info/', views.get_language_info, name='get_language_info'),
    
    # ÇEREZ YÖNETİMİ API'LERİ - dil-bağımsız (daha mantıklı)
    path('api/cookie-preferences/', views.save_cookie_preferences, name='save_cookie_preferences'),
    path('api/get-cookie-preferences/', views.get_cookie_preferences, name='get_cookie_preferences'),
    
    # Sitemap
    path('sitemap.xml', 
         cache_page(86400)(sitemap) if sitemaps else TemplateView.as_view(
             template_name="sitemap.xml", content_type="application/xml"),
         {'sitemaps': sitemaps} if sitemaps else {},
         name='django.contrib.sitemaps.views.sitemap'),
    
    path('robots.txt', cache_page(86400)(TemplateView.as_view(
         template_name="robots.txt", content_type="text/plain"))),
    
    path('katalog/', catalog_view, name='catalog_view'),
]

# Dil-bağımlı URL'ler (sadece site içeriği)
urlpatterns += i18n_patterns(
    path('', include('home.urls')),
    path('urunler/', include('products.urls')),
    path('galeri/', include('gallery.urls')),
    path('hakkimizda/', include('about.urls')),
    path('iletisim/', include('contact.urls')),
    path('reviews/', include('reviews.urls')),
    
    # YASAL SAYFALAR - dil-bağımlı
    path('yasal/<slug:slug>/', views.legal_page_detail, name='legal_page_detail'),
    
    prefix_default_language=True,
)

# Statik ve media dosyalar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug Toolbar URLs (opsiyonel - kurulu ise)
    try:
        import debug_toolbar
        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
        ] + urlpatterns
    except ImportError:
        pass  # debug_toolbar kurulu değilse sessizce atla

# Error handlers
handler400 = 'core.views.custom_400_view'
handler403 = 'core.views.custom_403_view' 
handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'