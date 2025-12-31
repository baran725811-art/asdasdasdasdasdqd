# about/views.py - DÜZELTİLMİŞ VERSİYON
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import About, Service, TeamMember
from dashboard.models import MediaMention
from django.core.paginator import Paginator


def about(request):
    """Ana hakkımızda sayfası - İlk About kaydını getirir"""
    
    try:
        about = About.objects.first()
        if not about:
            # Varsayılan değerlerle oluştur
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
    except Exception as e:
        raise Http404("Hakkımızda bilgisi bulunamadı")
    
    context = {
        'about': about,
        'media_mentions': MediaMention.objects.filter(is_active=True).order_by('-publish_date')[:6],
        'services': Service.objects.filter(is_active=True).order_by('order')[:4],  # Ana sayfada sadece 4 tane
        'team_members': TeamMember.objects.filter(is_active=True).order_by('order')[:4],  # Ana sayfada sadece 4 tane
        
        # SEO Meta bilgileri
        'meta_title': about.meta_title or about.title,
        'meta_description': about.meta_description or about.short_description,
        
        # İstatistikler
        'company_info': {
            'years_experience': about.years_experience,
            'completed_jobs': about.completed_jobs,
            'happy_customers': about.happy_customers,
            'total_services': about.total_services,
            'customer_satisfaction': about.customer_satisfaction,
        }
    }
    
    return render(request, 'about/about.html', context)

def about_detail(request, slug):
    """Belirli bir hakkımızda sayfası detayı"""
    about = get_object_or_404(About, slug=slug)
    
    context = {
        'about': about,
        'media_mentions': MediaMention.objects.filter(is_active=True).order_by('-publish_date')[:6],
        'services': Service.objects.filter(is_active=True).order_by('order'),
        'team_members': TeamMember.objects.filter(is_active=True).order_by('order'),
        
        # SEO Meta bilgileri
        'meta_title': about.meta_title or about.title,
        'meta_description': about.meta_description or about.short_description,
        
        # İstatistikler
        'company_info': {
            'years_experience': about.years_experience,
            'completed_jobs': about.completed_jobs,
            'happy_customers': about.happy_customers,
            'total_services': about.total_services,
            'customer_satisfaction': about.customer_satisfaction,
        }
    }
    
    return render(request, 'about/about_detail.html', context)

def services(request):
    """Tüm hizmetler listesi"""
    services = Service.objects.filter(is_active=True).order_by('order')
    
    context = {
        'services': services,
        'meta_title': 'Hizmetlerimiz - Profesyonel Hizmet Çözümleri',
        'meta_description': 'Geniş hizmet yelpazemiz ile ihtiyaçlarınıza en uygun çözümleri sunuyoruz.',
    }
    
    return render(request, 'about/services.html', context)

def service_detail(request, slug):
    """Belirli bir hizmet detayı"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    
    # İlgili diğer hizmetler
    related_services = Service.objects.filter(
        is_active=True
    ).exclude(pk=service.pk).order_by('order')[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
        
        # SEO Meta bilgileri
        'meta_title': service.meta_title or f"{service.title} - Hizmetlerimiz",
        'meta_description': service.meta_description or service.description[:160],
    }
    
    return render(request, 'about/sections/service_detail.html', context)

def team(request):
    """Tüm ekip üyeleri listesi"""
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    
    context = {
        'team_members': team_members,
        'meta_title': 'Ekibimiz - Uzman Kadromuz',
        'meta_description': 'Deneyimli ve uzman ekibimizle size en iyi hizmeti sunmak için buradayız.',
    }
    
    return render(request, 'about/team.html', context)

def team_detail(request, slug):
    """Belirli bir ekip üyesi detayı"""
    team_member = get_object_or_404(TeamMember, slug=slug, is_active=True)
    
    # Diğer ekip üyeleri
    other_members = TeamMember.objects.filter(
        is_active=True
    ).exclude(pk=team_member.pk).order_by('order')[:3]
    
    context = {
        'team_member': team_member,
        'other_members': other_members,
        
        # SEO Meta bilgileri
        'meta_title': team_member.meta_title or f"{team_member.name} - {team_member.position}",
        'meta_description': team_member.meta_description or team_member.bio[:160],
    }
    
    return render(request, 'about/team_detail.html', context)


def media_mentions_list(request):
    """Tüm basın haberlerini listeler"""
    media_mentions = MediaMention.objects.filter(is_active=True).order_by('-publish_date')
    
    # Sayfalama
    paginator = Paginator(media_mentions, 12)  # Sayfa başına 12 haber
    page_number = request.GET.get('page')
    media_mentions = paginator.get_page(page_number)
    
    context = {
        'media_mentions': media_mentions,
        'meta_title': 'Basın Haberleri - Medyada Biz',
        'meta_description': 'Şirketimizin basında yer alan haberlerini ve medya görünümlerini inceleyin.',
        'title': 'Basın Haberleri'
    }
    
    return render(request, 'about/media_mentions_list.html', context)