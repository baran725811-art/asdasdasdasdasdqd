# home/views.py - UPDATED VERSION
from django.shortcuts import render
from django.utils import translation
from .models import CarouselSlide
from about.models import About, Service, TeamMember
from products.models import Product
from gallery.models import Gallery
from dashboard.models import MediaMention
from reviews.models import Review

def home(request):
    """Ana sayfa view'ı - Featured Gallery düzeltmesi"""
    
    # About bilgilerini çek veya varsayılan oluştur
    try:
        about = About.objects.get(pk=1)
    except About.DoesNotExist:
        # Eğer About objesi yoksa varsayılan değerlerle oluştur
        about = About.objects.create(
            title='Hakkımızda',
            short_description='Profesyonel hizmet anlayışımızla sizlerleyiz.',
            mission='Müşterilerimize en iyi hizmeti sunmak.',
            vision='Sektörün lider firması olmak.',
            story='Yıllardır süregelen deneyimimizle hizmet veriyoruz.',
            years_experience=20,
            completed_jobs=5000,
            happy_customers=1000,
            total_services=10,
            customer_satisfaction=100,
        )
    
    # Context hazırla
    context = {
        # Ana carousel
        'carousel_slides': CarouselSlide.objects.filter(is_active=True).order_by('order')[:5],

        # ABOUT BİLGİLERİ
        'about': about,
        'company_info': {
            'years_experience': about.years_experience or 20,
            'completed_jobs': about.completed_jobs or 5000,
            'happy_customers': about.happy_customers or 1000,
            'total_services': about.total_services or 10,
            'customer_satisfaction': about.customer_satisfaction or 100,
        },
        
        # ✅ FEATURED GALERİ - HEM RESİM HEM VİDEO
        'latest_images': Gallery.objects.filter(
            is_active=True, 
            is_featured=True
        ).order_by('order', '-created_at')[:10],
        
        # Ürünler
        'featured_products': Product.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:9],
        
        # Basın haberleri
        'media_mentions': MediaMention.objects.filter(is_active=True).order_by('-publish_date')[:6],
        
        # Yorumlar
        'approved_reviews': Review.objects.filter(is_approved=True).order_by('-created_at')[:10],
        
        # Hizmetler
        'services': Service.objects.filter(is_active=True).order_by('order')[:6],
        
        # Ekip
        'team_members': TeamMember.objects.filter(is_active=True).order_by('order')[:6],
    }
    
    return render(request, 'home/index.html', context)