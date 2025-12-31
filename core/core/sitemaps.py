# core/sitemaps.py - GELİŞMİŞ SITEMAP OPTİMİZASYONU

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db import models

class StaticViewSitemap(Sitemap):
    """
    Statik sayfalar için gelişmiş sitemap
    """
    priority = 1.0
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'home:home',
            'products:product_list',
            'gallery:gallery_list',
            'about:about',
            'contact:contact',
        ]

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Cache'den last modified zamanını al
        cache_key = f'static_lastmod_{item}'
        lastmod = cache.get(cache_key)
        
        if lastmod is None:
            # Varsayılan olarak son 7 gün içinde güncelle
            lastmod = timezone.now() - timedelta(days=7)
            cache.set(cache_key, lastmod, 86400)  # 24 saat cache
        
        return lastmod

    def priority_map(self, item):
        priorities = {
            'home:home': 1.0,
            'products:product_list': 0.9,
            'gallery:gallery_list': 0.8,
            'about:about': 0.7,
            'contact:contact': 0.6,
        }
        return priorities.get(item, 0.5)

class ProductSitemap(Sitemap):
    """
    Ürün sitemap'i - SEO optimized
    """
    changefreq = "daily"
    priority = 0.8
    protocol = 'https'
    limit = 50000  # Google limiti

    def items(self):
        from products.models import Product
        return Product.objects.filter(
            is_active=True
        ).select_related('category').order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
    
    def priority(self, obj):
        # Öne çıkan ürünler daha yüksek öncelik
        if obj.is_featured:
            return 0.9
        return 0.7

class CategorySitemap(Sitemap):
    """
    Kategori sitemap'i
    """
    changefreq = "weekly"
    priority = 0.7
    protocol = 'https'

    def items(self):
        from products.models import Category
        return Category.objects.filter(
            is_active=True
        ).annotate(
            product_count=models.Count('product', filter=models.Q(product__is_active=True))
        ).filter(product_count__gt=0).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

    def priority(self, obj):
        # Ürün sayısına göre öncelik
        if hasattr(obj, 'product_count'):
            if obj.product_count > 10:
                return 0.8
            elif obj.product_count > 5:
                return 0.7
        return 0.6

class GallerySitemap(Sitemap):
    """
    Galeri sitemap'i
    """
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'

    def items(self):
        from gallery.models import Gallery
        return Gallery.objects.filter(is_active=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

    def priority(self, obj):
        if obj.is_featured:
            return 0.7
        return 0.5

class ServiceSitemap(Sitemap):
    """
    Hizmet sitemap'i
    """
    changefreq = "monthly"
    priority = 0.6
    protocol = 'https'

    def items(self):
        from about.models import Service
        return Service.objects.filter(is_active=True).order_by('order')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

class TeamSitemap(Sitemap):
    """
    Ekip sitemap'i
    """
    changefreq = "monthly"
    priority = 0.4
    protocol = 'https'

    def items(self):
        from about.models import TeamMember
        return TeamMember.objects.filter(is_active=True).order_by('order')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

class CarouselSitemap(Sitemap):
    """
    Ana sayfa carousel sitemap'i
    """
    changefreq = "weekly"
    priority = 0.3
    protocol = 'https'

    def items(self):
        try:
            from home.models import CarouselSlide
            return CarouselSlide.objects.filter(is_active=True).order_by('order')
        except ImportError:
            return []

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

class NewsSitemap(Sitemap):
    """
    Haber/Blog sitemap'i (gelecekte eklenebilir)
    """
    changefreq = "daily"
    priority = 0.8
    protocol = 'https'

    def items(self):
        # Blog/haber modeli eklendiğinde kullanılacak
        return []

# Sitemap index - Gelişmiş yapı
class SitemapIndex:
    """
    Sitemap yönetimi için yardımcı sınıf
    """
    
    @staticmethod
    def get_all_sitemaps():
        """Tüm sitemap'leri döndürür"""
        return {
            'static': StaticViewSitemap,
            'products': ProductSitemap,
            'categories': CategorySitemap,
            'gallery': GallerySitemap,
            'services': ServiceSitemap,
            'team': TeamSitemap,
            'carousel': CarouselSitemap,
        }
    
    @staticmethod
    def get_sitemap_stats():
        """Sitemap istatistikleri"""
        stats = {}
        
        try:
            from products.models import Product, Category
            from gallery.models import Gallery
            from about.models import Service, TeamMember
            
            stats['products'] = Product.objects.filter(is_active=True).count()
            stats['categories'] = Category.objects.filter(is_active=True).count()
            stats['gallery'] = Gallery.objects.filter(is_active=True).count()
            stats['services'] = Service.objects.filter(is_active=True).count()
            stats['team'] = TeamMember.objects.filter(is_active=True).count()
            stats['static_pages'] = 5
            
            try:
                from home.models import CarouselSlide
                stats['carousel'] = CarouselSlide.objects.filter(is_active=True).count()
            except ImportError:
                stats['carousel'] = 0
                
        except Exception as e:
        
        return stats