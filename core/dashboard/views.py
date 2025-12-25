#core\dashboard\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django_ratelimit.decorators import ratelimit
from .models import MediaMention, CustomerReview
from .forms import (MediaMentionForm, CategoryForm, ProductForm, 
                   CustomerReviewForm, AboutForm, GalleryForm, ServiceForm,
                   CarouselSlideForm, CategoryFormWithTranslation, AboutFormWithTranslation,    
                   ProductFormWithTranslation, GalleryFormWithTranslation,
                   CarouselSlideFormWithTranslation, ServiceFormWithTranslation, 
                   TeamMemberFormWithTranslation, MediaMentionFormWithTranslation)
from about.models import About, Service, TeamMember
from gallery.models import Gallery
from contact.models import Contact
from home.models import CarouselSlide
from products.models import Category, Product
from reviews.models import Review
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.db import transaction
from .forms import ProfileForm, BusinessSettingsForm, CustomPasswordChangeForm


from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from core.utils import check_cloudinary_storage

from axes.decorators import axes_dispatch
from axes.helpers import get_failure_limit
from axes.models import AccessAttempt
from django.contrib.auth import authenticate, login
from .forms import DashboardLoginForm
import logging

from .forms import TeamMemberForm 
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash
from django.db import models

# dashboard/views.py - eklenecek kısım
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Notification
from django.conf import settings
from django.urls import reverse_lazy, reverse 



# Login View

@axes_dispatch
def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # Rate limiting kontrolü
    was_limited = getattr(request, 'limited', False)
    
    # IP adresini al
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    ip_address = get_client_ip(request)
    
    # Başarısız deneme sayısını kontrol et
    try:
        attempts_count = AccessAttempt.objects.filter(
            ip_address=ip_address
        ).count()
    except:
        attempts_count = 0
    
    # 3 veya daha fazla başarısız denemede CAPTCHA göster
    show_captcha = True #attempts_count >= 3 or was_limited
    
    print(f"DEBUG: IP: {ip_address}, Attempts: {attempts_count}, Show CAPTCHA: {show_captcha}")  # DEBUG
    
    if request.method == 'POST':
        form = DashboardLoginForm(
            request.POST, 
            show_captcha=show_captcha, 
            request=request
        )
        
        if was_limited:
            messages.error(request, 'Çok fazla başarısız deneme. Lütfen birkaç dakika bekleyin.')
            return render(request, 'dashboard/login.html', {
                'form': form, 
                'show_captcha': True,
                'attempts': attempts_count,
                'max_attempts': 5,
            })
        
        if form.is_valid():
            user = form.cleaned_data.get('user')
            
            if user:
                login(request, user)
                
                try:
                    from axes.utils import reset
                    reset(request=request)
                except:
                    pass
                
                logger.info(f"Successful login: {user.username} from {ip_address}")
                messages.success(request, f'Hoş geldiniz {user.get_full_name() or user.username}!')
                
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Giriş bilgilerini kontrol edin.')
            logger.warning(f"Failed login attempt from {ip_address}")
    else:
        form = DashboardLoginForm(
            show_captcha=show_captcha, 
            request=request
        )
    
    print(f"DEBUG: Form has captcha: {'captcha' in form.fields}")  # DEBUG
    if 'captcha' in form.fields:
        print(f"DEBUG: CAPTCHA required: {form.fields['captcha'].required}")
        print(f"DEBUG: CAPTCHA widget: {type(form.fields['captcha'].widget)}")
        print(f"DEBUG: CAPTCHA widget attrs: {form.fields['captcha'].widget.attrs}")
    
    context = {
        'form': form,
        'show_captcha': show_captcha,
        'attempts': attempts_count if show_captcha else 0,
        'max_attempts': 5,
    }
    
    return render(request, 'dashboard/login.html', context)



# Dashboard Ana Sayfa
@staff_member_required(login_url='dashboard:dashboard_login')
def dashboard_home(request):
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import datetime, timedelta
    from core.models import SiteSettings
    
    site_settings = SiteSettings.get_current()
    
    # Temel istatistikler
    categories = Category.objects.annotate(product_count=Count('product')).order_by('name')
    rating_counts = Review.objects.values('rating').annotate(count=Count('rating')).order_by('rating')
    rating_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for item in rating_counts:
        rating_dict[item['rating']] = item['count']
    
    # Son 30 günün aktiviteleri
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_activities = []
    
    # Son eklenen ürünler
    recent_products = Product.objects.filter(created_at__gte=thirty_days_ago).order_by('-created_at')[:3]
    for product in recent_products:
        recent_activities.append({
            'type': 'product_added',
            'title': f'Yeni ürün eklendi: {product.name}',
            'description': f'{product.category.name} kategorisine eklendi',
            'time': product.created_at,
            'icon': 'fas fa-plus',
            'color': 'primary'
        })
    
    # Son yorumlar
    recent_reviews = Review.objects.filter(created_at__gte=thirty_days_ago).order_by('-created_at')[:3]
    for review in recent_reviews:
        recent_activities.append({
            'type': 'review_added',
            'title': f'{review.rating} yıldızlı yorum alındı',
            'description': f'{review.name} tarafından',
            'time': review.created_at,
            'icon': 'fas fa-star',
            'color': 'success'
        })
    
    # Son mesajlar
    recent_messages = Contact.objects.filter(created_at__gte=thirty_days_ago).order_by('-created_at')[:2]
    for message in recent_messages:
        recent_activities.append({
            'type': 'message_received',
            'title': f'Yeni mesaj: {message.subject}',
            'description': f'{message.name} tarafından gönderildi',
            'time': message.created_at,
            'icon': 'fas fa-envelope',
            'color': 'info'
        })
    
    # Aktiviteleri tarihe göre sırala
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:8]
    
    categories_with_counts = Category.objects.annotate(
        product_count=Count('product', filter=Q(product__is_active=True))
    ).filter(product_count__gt=0).order_by('-product_count')
    
    # Aylık istatistikler (son 6 ay)
    monthly_stats = []
    now = timezone.now()
    
    for i in range(6):
        # Her ayın başını hesapla
        if i == 0:
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            year = now.year
            month = now.month - i
            if month <= 0:
                month += 12
                year -= 1
            month_start = datetime(year, month, 1, tzinfo=now.tzinfo)
        
        # Ayın sonu
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        # O aydaki veriler
        products_count = Product.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end,
            is_active=True
        ).count()
        
        reviews_count = Review.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        messages_count = Contact.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%B'),
            'month_short': month_start.strftime('%b'),
            'products': products_count,
            'reviews': reviews_count,
            'messages': messages_count,
            'year': month_start.year
        })
    
    monthly_stats.reverse()
    
    # Debug çıktısı
    print(f"Monthly stats count: {len(monthly_stats)}")
    for stat in monthly_stats:
        print(f"{stat['month_short']}: {stat['products']} products, {stat['reviews']} reviews, {stat['messages']} messages")
    
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_reviews': Review.objects.count(),
        'total_media_mentions': MediaMention.objects.count(),
        'recent_products': Product.objects.order_by('-created_at')[:5],
        'recent_reviews': Review.objects.order_by('-created_at')[:5],
        'unread_messages': Contact.objects.filter(is_read=False).count(),
        'categories': categories,
        'rating_counts': rating_dict,
        'recent_activities': recent_activities,
        'monthly_stats': monthly_stats,
        'low_stock_products': Product.objects.filter(stock__lte=5, stock__isnull=False).count(),
        'pending_reviews': Review.objects.filter(is_approved=False).count(),
        'recent_unread_messages': Contact.objects.filter(is_read=False).order_by('-created_at')[:3],
        'recent_unapproved_reviews': Review.objects.filter(is_approved=False).order_by('-created_at')[:3],
        'has_notifications': Contact.objects.filter(is_read=False).exists() or Review.objects.filter(is_approved=False).exists(),
        'categories_with_counts': categories_with_counts,
        'translation_enabled': site_settings.translation_enabled,
        'activities_url': reverse('dashboard:activities_list'),
        'quick_actions': [
            {
                'title': 'Ürün Ekle',
                'description': 'Yeni ürün ekle',
                'icon': 'fas fa-plus',
                'url': reverse('dashboard:product_add'),
                'color': 'primary'
            },
            {
                'title': 'Kategoriler',
                'description': 'Kategori yönet',
                'icon': 'fas fa-tags',
                'url': reverse('dashboard:dashboard_categories'),
                'color': 'success'
            },
            {
                'title': 'Mesajlar',
                'description': 'Müşteri mesajları',
                'icon': 'fas fa-envelope',
                'url': reverse('dashboard:dashboard_messages'),
                'color': 'info'
            },
            {
                'title': 'Galeri',
                'description': 'Galeri yönet',
                'icon': 'fas fa-images',
                'url': reverse('dashboard:dashboard_gallery'),
                'color': 'warning'
            }
        ]
    }
    
    if request.GET.get('ajax'):
        return JsonResponse({
            'has_new_notifications': Contact.objects.filter(is_read=False).exists() or Review.objects.filter(is_approved=False).exists()
        })
    
    return render(request, 'dashboard/index.html', context)




@staff_member_required(login_url='dashboard:dashboard_login')
def chart_data_api(request, chart_id):
    from django.http import JsonResponse
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    period = int(request.GET.get('period', 7))
    end_date = timezone.now()
    
    if chart_id == 'monthlyChart':
        # Period'a göre aylık istatistikler
        monthly_stats = []
        
        for i in range(6):  # Son 6 ay
            if i == 0:
                month_start = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                year = end_date.year
                month = end_date.month - i
                if month <= 0:
                    month += 12
                    year -= 1
                month_start = datetime(year, month, 1, tzinfo=end_date.tzinfo)
            
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)
            
            products_count = Product.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end,
                is_active=True
            ).count()
            
            reviews_count = Review.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            messages_count = Contact.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            monthly_stats.append({
                'month_short': month_start.strftime('%b'),
                'products': products_count,
                'reviews': reviews_count,
                'messages': messages_count
            })
        
        monthly_stats.reverse()
        
        return JsonResponse({
            'labels': [stat['month_short'] for stat in monthly_stats],
            'datasets': [
                {
                    'label': 'Ürünler',
                    'data': [stat['products'] for stat in monthly_stats],
                    'borderColor': 'rgba(102, 126, 234, 1)',
                    'backgroundColor': 'rgba(102, 126, 234, 0.1)',
                    'tension': 0.4,
                    'fill': True,
                    'pointBackgroundColor': 'rgba(102, 126, 234, 1)',
                    'pointBorderColor': '#fff',
                    'pointBorderWidth': 2,
                    'pointRadius': 6
                },
                {
                    'label': 'Yorumlar',
                    'data': [stat['reviews'] for stat in monthly_stats],
                    'borderColor': 'rgba(17, 153, 142, 1)',
                    'backgroundColor': 'rgba(17, 153, 142, 0.1)',
                    'tension': 0.4,
                    'fill': True,
                    'pointBackgroundColor': 'rgba(17, 153, 142, 1)',
                    'pointBorderColor': '#fff',
                    'pointBorderWidth': 2,
                    'pointRadius': 6
                },
                {
                    'label': 'Mesajlar',
                    'data': [stat['messages'] for stat in monthly_stats],
                    'borderColor': 'rgba(255, 193, 7, 1)',
                    'backgroundColor': 'rgba(255, 193, 7, 0.1)',
                    'tension': 0.4,
                    'fill': True,
                    'pointBackgroundColor': 'rgba(255, 193, 7, 1)',
                    'pointBorderColor': '#fff',
                    'pointBorderWidth': 2,
                    'pointRadius': 6
                }
            ]
        })
    
    return JsonResponse({'error': 'Invalid chart ID'}, status=400)
# Hakkımızda Bölümü
@staff_member_required(login_url='dashboard:dashboard_login')
def about_edit(request):
    """Hakkımızda düzenleme - DÜZELTILMIŞ VERSİYON"""
    
    # Çeviri sistemi kontrol et - GALERİ BÖLÜMÜ GİBİ
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    # About objesini al veya oluştur
    try:
        about = About.objects.get(pk=1)
        print(f"✅ Mevcut About - ID: {about.id}, Years: {about.years_experience}")
    except About.DoesNotExist:
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
    
    if request.method == 'POST':
        print("\n=== POST İSTEĞİ ===")
        print(f"Gelen veriler: {dict(request.POST)}")
        
        # Form oluştur
        # Eski AboutForm yerine yeni AboutFormWithTranslation kullan
        form = AboutFormWithTranslation(
            request.POST, 
            request.FILES, 
            instance=about,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        if form.is_valid():
            print("✅ Form geçerli - kaydediliyor...")
            try:
                # Transaction ile kaydet
                with transaction.atomic():
                    # Değişiklikleri debug et
                    changed_fields = form.changed_data
                    print(f"Değişen alanlar: {changed_fields}")
                    
                    # Kaydet
                    saved_about = form.save()
                    
                    # Veritabanından tekrar oku
                    saved_about.refresh_from_db()
                    
                    print(f"✅ KAYDEDİLDİ - Years: {saved_about.years_experience}")
                    
                # AJAX response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Hakkımızda bilgileri başarıyla güncellendi!',
                        'about_id': saved_about.id,
                    })
                else:
                    messages.success(request, 'Hakkımızda bilgileri başarıyla güncellendi!')
                    return redirect('dashboard:dashboard_about_edit')
                    
            except Exception as e:
                print(f"❌ Hata: {str(e)}")
                import traceback
                traceback.print_exc()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Kaydetme hatası: {str(e)}'
                    })
        else:
            print("❌ Form geçersiz!")
            print(f"Hatalar: {dict(form.errors)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
    else:
        # GET request
        form = AboutFormWithTranslation(
            instance=about,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
    
    if translation_enabled and len(enabled_languages) > 1:
        about_with_translations = {
            'object': about,
            'translations': {}
        }

        for lang in enabled_languages:
            if lang != 'tr':
                about_with_translations['translations'][lang] = {
                    'title': getattr(about, f'title_{lang}', ''),
                    'short_description': getattr(about, f'short_description_{lang}', ''),
                    'mission': getattr(about, f'mission_{lang}', ''),
                    'vision': getattr(about, f'vision_{lang}', ''),
                    'story': getattr(about, f'story_{lang}', ''),
                }
    else:
        about_with_translations = None

    # Form tamamlanma durumunu hesapla
    completion_data = calculate_completion_status(about)

    context = {
        'form': form,
        'about': about,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        'about_with_translations': about_with_translations,
        'completion_percentage': completion_data['percentage'],
        'completed_fields': completion_data['completed'],
        'total_fields': completion_data['total'],
        'field_status': completion_data['fields'],
    }
    return render(request, 'dashboard/about/edit.html', context)


# ✅ YENİ YARDIMCI FONKSİYONLAR - EN SONA EKLENİYOR
def calculate_content_completion(about):
    """İçerik tamamlanma yüzdesini hesapla"""
    fields = ['title', 'short_description', 'mission', 'vision', 'story']
    completed = 0
    total = len(fields)

    for field in fields:
        value = getattr(about, field, None)
        if value and str(value).strip():
            completed += 1

    # İstatistik alanları
    stat_fields = ['years_experience', 'completed_jobs', 'happy_customers', 'total_services', 'customer_satisfaction']
    stat_completed = 0
    stat_total = len(stat_fields)

    for field in stat_fields:
        value = getattr(about, field, None)
        if value and value > 0:
            stat_completed += 1

    # Görsel
    image_completed = 1 if about.image else 0

    # Toplam hesaplama
    total_completed = completed + stat_completed + image_completed
    total_fields = total + stat_total + 1  # +1 için görsel

    return int((total_completed / total_fields) * 100)


def calculate_completion_status(about):
    """Detaylı form tamamlanma durumunu hesapla"""
    field_status = []
    completed_count = 0

    # 1. Sayfa Başlığı
    title_ok = bool(about.title and about.title.strip())
    field_status.append({
        'name': 'Sayfa Başlığı',
        'completed': title_ok,
        'badge': 'Tamam' if title_ok else 'Eksik',
        'reason': '' if title_ok else 'Başlık alanı boş'
    })
    if title_ok:
        completed_count += 1

    # 2. Kısa Açıklama
    desc_ok = bool(about.short_description and about.short_description.strip())
    field_status.append({
        'name': 'Kısa Açıklama',
        'completed': desc_ok,
        'badge': 'Tamam' if desc_ok else 'Eksik',
        'reason': '' if desc_ok else 'Kısa açıklama boş'
    })
    if desc_ok:
        completed_count += 1

    # 3. Ana Görsel
    image_ok = bool(about.image)
    field_status.append({
        'name': 'Ana Görsel',
        'completed': image_ok,
        'badge': 'Var' if image_ok else 'Yok',
        'reason': '' if image_ok else 'Görsel yüklenmemiş'
    })
    if image_ok:
        completed_count += 1

    # 4. Misyon
    mission_ok = bool(about.mission and about.mission.strip())
    field_status.append({
        'name': 'Misyon',
        'completed': mission_ok,
        'badge': 'Tamam' if mission_ok else 'Eksik',
        'reason': '' if mission_ok else 'Misyon metni boş'
    })
    if mission_ok:
        completed_count += 1

    # 5. Vizyon
    vision_ok = bool(about.vision and about.vision.strip())
    field_status.append({
        'name': 'Vizyon',
        'completed': vision_ok,
        'badge': 'Tamam' if vision_ok else 'Eksik',
        'reason': '' if vision_ok else 'Vizyon metni boş'
    })
    if vision_ok:
        completed_count += 1

    # 6. Hikaye
    story_ok = bool(about.story and about.story.strip())
    field_status.append({
        'name': 'Hikaye',
        'completed': story_ok,
        'badge': 'Tamam' if story_ok else 'Eksik',
        'reason': '' if story_ok else 'Hikaye metni boş'
    })
    if story_ok:
        completed_count += 1

    # 7. İstatistikler (5 alan)
    stat_fields = {
        'years_experience': 'Tecrübe Yılı',
        'completed_jobs': 'Tamamlanan İşler',
        'happy_customers': 'Mutlu Müşteri',
        'total_services': 'Toplam Hizmet',
        'customer_satisfaction': 'Müşteri Memnuniyeti'
    }
    stat_count = 0
    stat_missing = []
    for field_name, display_name in stat_fields.items():
        value = getattr(about, field_name, None)
        if value and value > 0:
            stat_count += 1
        else:
            stat_missing.append(display_name)

    all_stats_ok = stat_count == 5
    field_status.append({
        'name': 'İstatistikler',
        'completed': all_stats_ok,
        'badge': f'{stat_count}/5',
        'reason': f'Eksik: {", ".join(stat_missing)}' if stat_missing else ''
    })
    if all_stats_ok:
        completed_count += 1

    # Toplam alan sayısı: 7 (başlık, açıklama, görsel, misyon, vizyon, hikaye, istatistikler)
    total_fields = 7
    percentage = int((completed_count / total_fields) * 100)

    return {
        'percentage': percentage,
        'completed': completed_count,
        'total': total_fields,
        'fields': field_status
    }


def calculate_translation_completion(about, enabled_languages):
    """Çeviri tamamlanma yüzdesini hesapla"""
    if len(enabled_languages) <= 1:
        return 100  # Sadece Türkçe varsa %100
    
    translatable_fields = ['title', 'short_description', 'mission', 'vision', 'story']
    total_fields = len(translatable_fields) * len(enabled_languages)
    completed_fields = 0
    
    for lang in enabled_languages:
        for field in translatable_fields:
            if lang == 'tr':
                # Türkçe alanlar
                value = getattr(about, field, None)
            else:
                # Çeviri alanları
                translated_field = f"{field}_{lang}"
                value = getattr(about, translated_field, None)
            
            if value and str(value).strip():
                completed_fields += 1
    
    return int((completed_fields / total_fields) * 100)




# Mesajlar ve Yorumlar
from contact.models import Contact
from reviews.models import Review  # Doğru import
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

@staff_member_required(login_url='dashboard:dashboard_login')
def messages_list(request):
    # Toplu okundu işaretleme kontrolü
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        unread_count = Contact.objects.filter(is_read=False).update(is_read=True)
        messages.success(request, f'{unread_count} mesaj okundu olarak işaretlendi.')
        return redirect('dashboard:dashboard_messages')
    
    # Tek mesaj okundu işaretleme
    if request.method == 'POST' and 'mark_read' in request.POST:
        message_id = request.POST.get('mark_read')
        try:
            message = Contact.objects.get(id=message_id, is_read=False)
            message.is_read = True
            message.save()
            messages.success(request, 'Mesaj okundu olarak işaretlendi.')
        except Contact.DoesNotExist:
            messages.error(request, 'Mesaj bulunamadı.')
        return redirect('dashboard:dashboard_messages')
    
    # Mesajları getir - okunmamışlar önce
    contact_messages = Contact.objects.all().order_by('is_read', '-created_at')
    customer_reviews = Review.objects.all().order_by('-created_at')
    
    # İstatistikler
    unread_count = Contact.objects.filter(is_read=False).count()
    pending_reviews = Review.objects.filter(is_approved=False).count()  # Doğru hesaplama
    approved_reviews = Review.objects.filter(is_approved=True).count()
    
    # Ortalama puan hesaplama
    reviews_with_rating = Review.objects.filter(is_approved=True)
    avg_rating = reviews_with_rating.aggregate(
        avg_rating=models.Avg('rating')
    )['avg_rating'] or 0
    
    # GET parametresi ile mesaj okundu olarak işaretlenebilir
    # Mesaj detayı görüntülendiğinde otomatik okundu işaretle
    if request.method == 'GET' and 'view_message' in request.GET:
        message_id = request.GET.get('view_message')
        try:
            message = Contact.objects.get(id=message_id, is_read=False)
            message.is_read = True
            message.save()
        except Contact.DoesNotExist:
            pass

    # Manuel okundu işaretleme
    if request.method == 'POST' and 'mark_single_read' in request.POST:
        message_id = request.POST.get('mark_single_read')
        try:
            message = Contact.objects.get(id=message_id, is_read=False)
            message.is_read = True
            message.save()
            messages.success(request, 'Mesaj okundu olarak işaretlendi.')
            return redirect('dashboard:dashboard_messages')
        except Contact.DoesNotExist:
            pass
    
    # Toplu okundu işaretleme
    if request.POST.get('mark_all_read'):
        Contact.objects.filter(is_read=False).update(is_read=True)
        messages.success(request, 'Tüm mesajlar okundu olarak işaretlendi.')
        return redirect('dashboard:dashboard_messages')
    
    context = {
        'contact_messages': contact_messages,
        'customer_reviews': customer_reviews,
        'unread_count': unread_count,
        'pending_reviews': pending_reviews,
        'approved_reviews': approved_reviews,
        'avg_rating': round(avg_rating, 1),

        # Table için gerekli header ve row verileri
        'contact_table_headers': [
            {'title': 'İsim', 'icon': 'fas fa-user'},
            {'title': 'Konu', 'icon': 'fas fa-envelope'},
            {'title': 'E-posta', 'icon': 'fas fa-at'},
            {'title': 'Tarih', 'width': '120px'},
            {'title': 'Durum', 'width': '100px', 'class': 'text-center'},
            {'title': 'İşlemler', 'width': '150px', 'class': 'text-center'},
        ],

        'contact_table_rows': [
            {
                'id': message.id,
                'name': message.name,
                'subject': message.subject,
                'email': message.email,
                'created_at': message.created_at,
                'is_read': message.is_read,
            }
            for message in contact_messages
        ]
    }
    return render(request, 'dashboard/messages/list.html', context)

# Yorum durumu değiştirme view'ını ekle
@staff_member_required(login_url='dashboard:dashboard_login')
def review_status_toggle(request, id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=id)
        review.is_approved = not review.is_approved
        review.save()
        
        status = "onaylandı" if review.is_approved else "onay bekliyor"
        messages.success(request, f'Yorum {status} durumuna getirildi.')
    
    return redirect('dashboard:dashboard_messages')

# Mesaj silme view'ını ekle  
@staff_member_required(login_url='dashboard:dashboard_login')
def message_delete(request, pk):
    if request.method == 'POST':
        message = get_object_or_404(Contact, pk=pk)
        message.delete()
        messages.success(request, 'Mesaj başarıyla silindi.')
    
    return redirect('dashboard:dashboard_messages')

# Yorum silme view'ını ekle
@staff_member_required(login_url='dashboard:dashboard_login') 
def review_delete(request, id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=id)
        review.delete()
        messages.success(request, 'Yorum başarıyla silindi.')
    
    return redirect('dashboard:dashboard_messages')

# dashboard/views.py'a ekleyin
@staff_member_required(login_url='dashboard:dashboard_login')
def message_delete(request, pk):
    message = get_object_or_404(Contact, pk=pk)
    message.delete()
    messages.success(request, 'Mesaj başarıyla silindi.')
    return redirect('dashboard:dashboard_messages')

# Galeri Yönetimi
# dashboard/views.py - gallery_list fonksiyonunu güncelleyin:

@staff_member_required(login_url='dashboard:dashboard_login')
@never_cache
def gallery_list(request):
    from django.db.models import Q
    from django.utils import timezone
    from datetime import timedelta
    from django.http import JsonResponse
    
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    # Filtreleme parametreleri
    search = request.GET.get('search', '').strip()
    media_type = request.GET.get('media_type', '')
    status = request.GET.get('status', '')
    ordering = request.GET.get('ordering', '-order')
    
    # Başlangıç queryset
    galleries = Gallery.objects.all()
    
    # Filtreleme uygula
    if search:
        galleries = galleries.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    if media_type:
        galleries = galleries.filter(media_type=media_type)
    
    if status == 'active':
        galleries = galleries.filter(is_active=True)
    elif status == 'inactive':
        galleries = galleries.filter(is_active=False)
    elif status == 'featured':
        galleries = galleries.filter(is_featured=True)
    
    # Sıralama uygula
    if ordering:
        galleries = galleries.order_by(ordering)
    else:
        galleries = galleries.order_by('-order', '-created_at')
    
    # İstatistikleri hesapla
    total_count = Gallery.objects.count()
    active_count = Gallery.objects.filter(is_active=True).count()
    featured_count = Gallery.objects.filter(is_featured=True).count()
    
    # Son 7 günde eklenen öğe sayısı
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_count = Gallery.objects.filter(created_at__gte=seven_days_ago).count()
    
    # Media type options for form
    media_type_options = [
        {'value': 'image', 'label': 'Resim'},
        {'value': 'video', 'label': 'Video'},
    ]
    
    # Table configuration - YENİ EKLENEN
    galleries_table_config = {
        'title': 'Galeri Listesi',
        'icon': 'fas fa-list',
        'search_placeholder': 'Galeri ara...',
        'search_id': 'gallerySearch',
        'table_id': 'galleriesTable',
        'model_name': 'Gallery',
        'model_name_lower': 'gallery',
        'add_button_text': 'Yeni Öğe Ekle',
        'empty_icon': 'fas fa-images',
        'empty_title': 'Henüz galeri öğesi eklenmemiş',
        'empty_message': 'İlk galeri öğenizi ekleyerek başlayın',
        'empty_action_attrs': 'data-bs-toggle="modal" data-bs-target="#addGalleryModal"'
    }
    
    # Table headers - YENİ EKLENEN  
    galleries_table_headers = [
        {'title': 'ID', 'width': '60px', 'class': 'text-center'},
        {'title': 'Görsel', 'width': '80px', 'class': 'text-center'},
        {'title': 'Başlık', 'icon': 'fas fa-heading'},
        {'title': 'Tür', 'icon': 'fas fa-photo-video', 'width': '100px'},
        {'title': 'Durum', 'width': '120px', 'class': 'text-center'},
        {'title': 'Sıralama', 'width': '80px', 'class': 'text-center'},
        {'title': 'İşlemler', 'width': '150px', 'class': 'text-center'},
    ]
    
    # Modal configuration - YENİ EKLENEN
    galleries_modal_config = {
        'model_name': 'Gallery',
        'model_name_lower': 'gallery',
        'add_title': 'Yeni Galeri Öğesi Ekle',
        'edit_title': 'Galeri Öğesi Düzenle',
        'view_title': 'Galeri Detayları',
        'save_text': 'Galeri Öğesini Kaydet',
        'item_type': 'galeri öğesi',
        'delete_warning': 'Bu galeri öğesi kalıcı olarak silinecek!',
        'add_url': reverse('dashboard:gallery_add'),
        'edit_url_pattern': '/dashboard/gallery/edit/',
        'size': 'modal-xl',
        'view_size': 'modal-lg'
    }
    
    # AJAX isteği kontrolü
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX isteği için sadece galeri öğelerini döndür
        from django.template.loader import render_to_string
        
        gallery_html = render_to_string('dashboard/gallery/gallery_items.html', {
            'galleries': galleries
        })
        
        return JsonResponse({
            'success': True,
            'gallery_html': gallery_html,
            'total_count': galleries.count(),
            'active_count': galleries.filter(is_active=True).count(),
            'featured_count': galleries.filter(is_featured=True).count(),
        })
    galleries_with_translations = []
    for gallery in galleries:
        gallery_data = {
            'object': gallery,
            'translations': {}
        }
        
        # Her dil için çeviri verilerini al
        for lang in enabled_languages:
            if lang != 'tr':  # Ana dil değilse
                gallery_data['translations'][lang] = {
                    'title': getattr(gallery, f'title_{lang}', ''),
                    'description': getattr(gallery, f'description_{lang}', ''),
                    'alt_text': getattr(gallery, f'alt_text_{lang}', ''),
                }
        
        galleries_with_translations.append(gallery_data)
    context = {
        'galleries': galleries,
        'total_count': total_count,
        'active_count': active_count,
        'featured_count': featured_count,
        'recent_count': recent_count,
        'media_type_options': media_type_options,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        'galleries_table_config': galleries_table_config,      # YENİ
        'galleries_table_headers': galleries_table_headers,    # YENİ
        'galleries_modal_config': galleries_modal_config,      # YENİ
        'galleries_with_translations': galleries_with_translations,
    }

    return render(request, 'dashboard/gallery/list.html', context)




# dashboard/views.py - gallery_add fonksiyonunu güncelleyin:
@staff_member_required(login_url='dashboard:dashboard_login')
def gallery_add(request):
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        print("=== GALLERY ADD POST İSTEĞİ ===")
        print(f"POST verileri: {dict(request.POST)}")
        print(f"Dosyalar: {dict(request.FILES)}")
        
        form = GalleryFormWithTranslation(
            request.POST,
            request.FILES,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        if form.is_valid():
            try:
                # ✅ ADIM 1: Form'u kaydet (commit=False ile)
                gallery_item = form.save(commit=False)
                gallery_item.save()  # Önce instance'ı kaydet ki ID oluşsun
                
                # ✅ ADIM 2: ORİJİNAL GÖRSELİ KAYDET (Base64'ten)
                original_image_data = request.POST.get('original_image_data')
                if original_image_data and 'base64,' in original_image_data:
                    import base64
                    from django.core.files.base import ContentFile
                    import uuid
                    
                    format, imgstr = original_image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    original_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'original_{uuid.uuid4()}.{ext}'
                    )
                    
                    # ✅ Cloudinary field için doğru yöntem
                    gallery_item.image = original_file
                    gallery_item.save()
                
                # ✅ ADIM 3: KIRPILMIŞ GÖRSELİ KAYDET
                # ✅ ADIM 3: KIRPILMIŞ GÖRSELİ KAYDET
                if 'cropped_image' in request.FILES:
                    gallery_item.cropped_image = request.FILES['cropped_image']
                    gallery_item.save()

                
                print(f"✅ GALERİ ÖĞESİ BAŞARIYLA KAYDEDİLDİ! ID: {gallery_item.id}, Title: {gallery_item.title}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Galeri öğesi "{gallery_item.title}" başarıyla eklendi.',
                        'item_id': gallery_item.id,
                        'redirect_url': reverse('dashboard:dashboard_gallery')
                    })
                else:
                    messages.success(request, f'Galeri öğesi "{gallery_item.title}" başarıyla eklendi.')
                    return redirect('dashboard:dashboard_gallery')
                    
            except Exception as e:
                print(f"❌ Kaydetme hatası: {str(e)}")
                import traceback
                traceback.print_exc()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Kaydetme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Kaydetme hatası: {str(e)}')
        else:
            print("❌ Form geçersiz!")
            print(f"Hatalar: {dict(form.errors)}")
            
            error_messages = []
            for field, errors in form.errors.items():
                if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                    lang_code = field.split('_')[-1]
                    lang_name = {
                        'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                        'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                    }.get(lang_code, lang_code.upper())
                    for error in errors:
                        error_msg = f'{field.replace(f"_{lang_code}", "").title()} {lang_name} çevirisi zorunludur.'
                        messages.error(request, error_msg)
                        error_messages.append(error_msg)
                else:
                    for error in errors:
                        error_msg = f'{field}: {error}'
                        messages.error(request, error_msg)
                        error_messages.append(error_msg)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Form hatası',
                    'errors': dict(form.errors),
                    'error_messages': error_messages
                })
    
    return redirect('dashboard:dashboard_gallery')


@staff_member_required(login_url='dashboard:dashboard_login')
def gallery_edit(request, pk):
    gallery_item = get_object_or_404(Gallery, pk=pk)
    
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    if request.method == 'POST':
        form = GalleryFormWithTranslation(
            request.POST, 
            request.FILES, 
            instance=gallery_item,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        if form.is_valid():
            try:
                # ✅ ADIM 1: Form'u kaydet
                gallery_item = form.save(commit=False)
                gallery_item.save()
                
                # ✅ ADIM 2: ORİJİNAL GÖRSELİ KAYDET (Base64'ten)
                original_image_data = request.POST.get('original_image_data')
                if original_image_data and 'base64,' in original_image_data:
                    import base64
                    from django.core.files.base import ContentFile
                    import uuid
                    
                    format, imgstr = original_image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    
                    original_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'original_{uuid.uuid4()}.{ext}'
                    )
                    
                    # ✅ Cloudinary field için doğru yöntem
                    gallery_item.image = original_file
                    gallery_item.save()
                
                # ✅ ADIM 3: KIRPILMIŞ GÖRSELİ KAYDET
                if 'cropped_image' in request.FILES:
                    gallery_item.cropped_image = request.FILES['cropped_image']
                    gallery_item.save()

                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Galeri öğesi "{gallery_item.title}" başarıyla güncellendi.',
                        'item_id': gallery_item.id,
                    })
                else:
                    messages.success(request, f'"{gallery_item.title}" başarıyla güncellendi.')
                    return redirect('dashboard:dashboard_gallery')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Güncelleme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Güncelleme hatası: {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
            else:
                messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
    
    return redirect('dashboard:dashboard_gallery')




@staff_member_required(login_url='dashboard:dashboard_login')
def gallery_delete(request, pk):
    """Galeri öğesi silme - Düzeltilmiş versiyon"""
    gallery_item = get_object_or_404(Gallery, pk=pk)
    gallery_title = gallery_item.title
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Görsel dosyasını da sil
                if gallery_item.image:
                    try:
                        import os
                        if os.path.isfile(gallery_item.image.path):
                            os.remove(gallery_item.image.path)
                    except:
                        pass  # Dosya silme hatası önemli değil
                
                gallery_item.delete()
                messages.success(request, f'"{gallery_title}" galeri öğesi başarıyla silindi.')
                
                # AJAX isteği kontrolü
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'"{gallery_title}" galeri öğesi başarıyla silindi.'
                    })
                    
        except Exception as e:
            error_message = f'Silme işlemi sırasında hata oluştu: {str(e)}'
            messages.error(request, error_message)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
    
    return redirect('dashboard:dashboard_gallery')

# Basın Bölümü

@staff_member_required(login_url='dashboard:dashboard_login')
def media_mentions_list(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    # CACHE'i önlemek için fresh queryset al
    mentions = MediaMention.objects.select_related().all().order_by('-publish_date')
    
    # ✅ İSTATİSTİKLERİ HESAPLA
    total_mentions = mentions.count()
    active_mentions_count = mentions.filter(is_active=True).count()
    inactive_mentions_count = mentions.filter(is_active=False).count()
    
    form = MediaMentionFormWithTranslation(
        translation_enabled=translation_enabled,
        enabled_languages=enabled_languages,
        user=request.user
    )
    
    mentions_with_translations = []
    for mention in mentions:
        # Database'den fresh data çek
        fresh_mention = MediaMention.objects.get(pk=mention.pk)
        
        mention_data = {
            'object': fresh_mention,
            'translations': {}
        }

        # Her dil için çeviri verilerini AL - FRESH DATA
        for lang in enabled_languages:
            if lang != 'tr':
                mention_data['translations'][lang] = {
                    'title': getattr(fresh_mention, f'title_{lang}', ''),
                    'source': getattr(fresh_mention, f'source_{lang}', ''),
                    'description': getattr(fresh_mention, f'description_{lang}', ''),
                }

        mentions_with_translations.append(mention_data)
        
    context = {
        'mentions': mentions,
        'mentions_with_translations': mentions_with_translations,
        'form': form,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        # ✅ İSTATİSTİKLER EKLENDİ
        'total_mentions': total_mentions,
        'active_mentions_count': active_mentions_count,
        'inactive_mentions_count': inactive_mentions_count,
    }
    return render(request, 'dashboard/media_mentions/list.html', context)
@staff_member_required(login_url='dashboard:dashboard_login')
def media_mention_add(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        print("=== MEDIA MENTION POST İSTEĞİ BAŞLADI ===")
        print("POST verileri:", dict(request.POST))
        
        form = MediaMentionFormWithTranslation(
            request.POST, 
            request.FILES,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        if form.is_valid():
            print("✅ Form geçerli, kaydediliyor...")
            try:
                saved_mention = form.save()
                print("✅ BAŞARIYLA KAYDEDİLDİ! ID:", saved_mention.id)
                messages.success(request, 'Basın haberi başarıyla eklendi.')
                return redirect('dashboard:dashboard_media_mentions')
            except Exception as e:
                print("❌ Kaydetme hatası:", str(e))
                messages.error(request, f'Kaydetme hatası: {str(e)}')
        else:
            print("❌ Form geçersiz!")
            print("Form hataları:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # GET request - redirect to list page (modal'da açılacak)
    return redirect('dashboard:dashboard_media_mentions')

# dashboard/views.py - media_mention_edit debug versiyonu

# dashboard/views.py - media_mention_edit fonksiyonu - Template compatible versiyonu

@staff_member_required(login_url='dashboard:dashboard_login')
def media_mention_edit(request, pk):
    mention = get_object_or_404(MediaMention, pk=pk)
    
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        print("=== MEDIA MENTION EDIT POST İSTEĞİ ===")
        print("POST verileri:", dict(request.POST))
        
        form = MediaMentionFormWithTranslation(
            request.POST, 
            request.FILES, 
            instance=mention,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        if form.is_valid():
            print("✅ Form geçerli, güncelleniyor...")
            try:
                saved_mention = form.save()
                print(f"✅ GÜNCELLEME BAŞARILI! URL: {saved_mention.url}, Date: {saved_mention.publish_date}")
                
                messages.success(request, f'Basın haberi "{saved_mention.title}" başarıyla güncellendi.')
                return redirect('dashboard:dashboard_media_mentions')
                
            except Exception as e:
                print("❌ Güncelleme hatası:", str(e))
                import traceback
                traceback.print_exc()
                messages.error(request, f'Güncelleme hatası: {str(e)}')
        else:
            print("❌ Form geçersiz!")
            print("Form hataları:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # GET request - Template'e normal render
    return redirect('dashboard:dashboard_media_mentions')

@staff_member_required(login_url='dashboard:dashboard_login')
def media_mention_delete(request, pk):
    mention = get_object_or_404(MediaMention, pk=pk)
    if request.method == 'POST':
        try:
            mention.delete()
            messages.success(request, 'Basın haberi silindi.')
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
    return redirect('dashboard:dashboard_media_mentions')  # Doğru URL adı

# Kategori Yönetimi
@staff_member_required(login_url='dashboard:dashboard_login')
def categories_list(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    categories = Category.objects.all().order_by('name')
    form = CategoryFormWithTranslation(
        translation_enabled=translation_enabled,
        enabled_languages=enabled_languages,
        user=request.user
    )
    
    categories_with_translations = []
    for category in categories:
        category_data = {
            'object': category,
            'translations': {}
        }
        
        # Her dil için çeviri verilerini al
        for lang in enabled_languages:
            if lang != 'tr':  # Ana dil değilse
                category_data['translations'][lang] = {
                    'name': getattr(category, f'name_{lang}', ''),
                    'description': getattr(category, f'description_{lang}', ''),
                }
        
        categories_with_translations.append(category_data)
    
    context = {
        'categories': categories,
        'form': form,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        'categories_with_translations': categories_with_translations,  # YENİ EKLENEN
    }
    return render(request, 'dashboard/categories/list.html', context)

@staff_member_required(login_url='dashboard:dashboard_login')
def category_add(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        form = CategoryFormWithTranslation(
            request.POST,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        if form.is_valid():
            try:
                category = form.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Kategori "{category.name}" başarıyla eklendi.',
                        'item_id': category.id,
                        'redirect_url': reverse('dashboard:categories_list')
                    })
                else:
                    messages.success(request, 'Kategori eklendi.')
                    return redirect('dashboard:dashboard_categories')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Kaydetme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Kaydetme hatası: {str(e)}')
        else:
            # Form geçersiz - AJAX ve normal request için hata handling
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
            else:
                # Çeviri hatalarını göster
                for field, errors in form.errors.items():
                    if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                        for error in errors:
                            lang_code = field.split('_')[-1]
                            lang_name = {
                                'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                                'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                            }.get(lang_code, lang_code.upper())
                            field_name = field.replace(f'_{lang_code}', '')
                            messages.error(request, f'{field_name.title()} {lang_name} çevirisi zorunludur.')
                    else:
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
    
    # GET request - redirect to list
    return redirect('dashboard:dashboard_categories')

@staff_member_required(login_url='dashboard:dashboard_login')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        form = CategoryFormWithTranslation(
            request.POST, 
            instance=category,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        if form.is_valid():
            try:
                category = form.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Kategori "{category.name}" başarıyla güncellendi.',
                        'item_id': category.id,
                    })
                else:
                    messages.success(request, 'Kategori güncellendi.')
                    return redirect('dashboard:dashboard_categories')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Güncelleme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Güncelleme hatası: {str(e)}')
        else:
            # Form geçersiz - AJAX ve normal request için hata handling
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
            else:
                # Çeviri hatalarını göster
                for field, errors in form.errors.items():
                    if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                        for error in errors:
                            lang_code = field.split('_')[-1]
                            lang_name = {
                                'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                                'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                            }.get(lang_code, lang_code.upper())
                            field_name = field.replace(f'_{lang_code}', '')
                            messages.error(request, f'{field_name.title()} {lang_name} çevirisi zorunludur.')
                    else:
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                            
                messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
    
    # GET request - redirect to list (modal'da açılıyor)
    return redirect('dashboard:dashboard_categories')

@staff_member_required(login_url='dashboard:dashboard_login')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category_name = category.name
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                category.delete()
                messages.success(request, f'Kategori "{category_name}" başarıyla silindi.')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Kategori "{category_name}" başarıyla silindi.'
                    })
                    
        except Exception as e:
            error_message = f'Silme işlemi sırasında hata oluştu: {str(e)}'
            messages.error(request, error_message)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
    
    return redirect('dashboard:dashboard_categories')

# Ürün Yönetimi Products


@staff_member_required(login_url='dashboard:dashboard_login')
def products_list(request):
    from django.db.models import Q, Count, Sum, Avg
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from urllib.parse import urlencode
    
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    # ===== FİLTRE PARAMETRELERİNİ AL =====
    category_id = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    status = request.GET.get('status', '')
    featured = request.GET.get('featured', '')
    stock_status = request.GET.get('stock_status', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    search = request.GET.get('search', '').strip()
    ordering = request.GET.get('ordering', '-created_at')
    per_page = int(request.GET.get('per_page', 20))

    # ===== QUERYSET OLUŞTUR =====
    products = Product.objects.select_related('category').all()

    # ===== FİLTRELEMELERİ UYGULA =====
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(brand__icontains=search) |
            Q(category__name__icontains=search)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if brand:
        products = products.filter(brand__icontains=brand)

    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)

    if featured == 'yes':
        products = products.filter(is_featured=True)
    elif featured == 'no':
        products = products.filter(is_featured=False)

    if stock_status:
        if stock_status == 'in_stock':
            products = products.filter(stock__gt=0)
        elif stock_status == 'low_stock':
            products = products.filter(stock__lte=5, stock__gt=0)
        elif stock_status == 'out_of_stock':
            products = products.filter(stock=0)
        elif stock_status == 'no_tracking':
            products = products.filter(stock__isnull=True)

    # Fiyat aralığı
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass

    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # ===== SIRALAMA =====
    valid_orderings = [
        'name', '-name', 'price', '-price', 'stock', '-stock',
        'created_at', '-created_at', 'category__name', '-category__name'
    ]
    if ordering in valid_orderings:
        products = products.order_by(ordering)
    else:
        products = products.order_by('-created_at')

    # ===== SAYFALAMA =====
    paginator = Paginator(products, per_page)
    page = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # ===== ÇEVİRİ VERİLERİ =====
    products_with_translations = []
    for product in page_obj:
        product_data = {
            'object': product,
            'translations': {}
        }
        
        for lang in enabled_languages:
            if lang != 'tr':
                product_data['translations'][lang] = {
                    'name': getattr(product, f'name_{lang}', ''),
                    'description': getattr(product, f'description_{lang}', ''),
                    'meta_title': getattr(product, f'meta_title_{lang}', ''),
                    'meta_description': getattr(product, f'meta_description_{lang}', ''),
                }
        
        products_with_translations.append(product_data)

    # ===== MEVCUT TEMPLATE İÇİN VERİLERİ HAZIRLA =====
    
    # Kategoriler ve markalar
    categories = Category.objects.all().order_by('name')
    category_options = [
        {'value': cat.id, 'label': cat.name} 
        for cat in categories
    ]

    # Mevcut markalar
    brands = Product.objects.values_list('brand', flat=True).distinct().exclude(brand__isnull=True).exclude(brand='')
    brand_options = [
        {'value': brand, 'label': brand}
        for brand in sorted(brands) if brand
    ]

    # ===== FİLTER LİSTESİ (MEVCUT TEMPLATE İÇİN) =====
    filters = []
    
    # Arama filtresi
    filters.append({
        'name': 'search',
        'type': 'search',
        'label': 'Ürün Ara',
        'placeholder': 'Ürün adı, kodu veya marka...',
        'value': search,
        'width': 4
    })
    
    # Kategori filtresi
    filters.append({
        'name': 'category',
        'type': 'select',
        'label': 'Kategori',
        'icon': 'fas fa-tags',
        'value': category_id,
        'options': [{'value': '', 'label': 'Tüm Kategoriler'}] + category_options,
        'width': 2
    })
    
    # Marka filtresi
    filters.append({
        'name': 'brand',
        'type': 'select',
        'label': 'Marka',
        'icon': 'fas fa-tag',
        'value': brand,
        'options': [{'value': '', 'label': 'Tüm Markalar'}] + brand_options,
        'width': 2
    })
    
    # Durum filtresi
    filters.append({
        'name': 'status',
        'type': 'select',
        'label': 'Durum',
        'icon': 'fas fa-toggle-on',
        'value': status,
        'options': [
            {'value': '', 'label': 'Tüm Durumlar'},
            {'value': 'active', 'label': 'Aktif'},
            {'value': 'inactive', 'label': 'Pasif'}
        ],
        'width': 2
    })
    
    # Stok durumu filtresi
    filters.append({
        'name': 'stock_status',
        'type': 'select',
        'label': 'Stok',
        'icon': 'fas fa-warehouse',
        'value': stock_status,
        'options': [
            {'value': '', 'label': 'Tüm Stoklar'},
            {'value': 'in_stock', 'label': 'Stokta Var'},
            {'value': 'low_stock', 'label': 'Düşük Stok'},
            {'value': 'out_of_stock', 'label': 'Stokta Yok'}
        ],
        'width': 2
    })

    # ===== URL PARAMETRELERİNİ KORUMA =====
    url_params_dict = request.GET.copy()
    if 'page' in url_params_dict:
        del url_params_dict['page']  # Sayfa numarasını çıkar
    
    url_params = '&' + url_params_dict.urlencode() if url_params_dict else ''

    # ===== İSTATİSTİKLER =====
    all_products = Product.objects.all()
    
    total_value = all_products.filter(price__isnull=False).aggregate(
        total=Sum('price')
    )['total'] or 0
    
    low_stock_count = all_products.filter(
        stock__lte=5, 
        stock__gt=0
    ).count()
    
    avg_price = all_products.filter(price__isnull=False).aggregate(
        avg=Avg('price')
    )['avg'] or 0

    # ===== CONTEXT =====
    context = {
        # Sayfalanmış ürünler
        'products': page_obj,
        'page_obj': page_obj,  # Pagination template için
        'url_params': url_params,  # URL parametrelerini koruma için
        
        # Çeviri verileri
        'products_with_translations': products_with_translations,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        
        # Filtreler (mevcut template için)
        'filters': filters,
        'product_filters': filters,
        # Diğer veriler
        'categories': categories,
        'category_options': category_options,
        'brand_options': brand_options,
        
        # İstatistikler
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'avg_price': avg_price,
        'active_products_count': all_products.filter(is_active=True).count(),
        'products_count': paginator.count,
    }
    
    return render(request, 'dashboard/products/list.html', context)











@staff_member_required(login_url='dashboard:dashboard_login')
def product_add(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        form = ProductFormWithTranslation(
            request.POST, 
            request.FILES,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        if form.is_valid():
            try:
                # ✅ DÜZELTME: Önce form'u commit=True ile kaydet (slug oluşsun)
                product = form.save(commit=True)
                
                # ✅ Product None kontrolü
                if product is None:
                    raise ValueError("Form save işlemi başarısız oldu")
                
                # ✅ KIRPILMIŞ GÖRSELİ KAYDET (Form'dan gelir)
                                
                cropped_saved = False
                if 'image' in request.FILES:
                    product.cropped_image = request.FILES['image']
                    cropped_saved = True

                # ✅ ORİJİNAL GÖRSELİ KAYDET (Base64'ten)
                original_saved = False
                original_image_data = request.POST.get('original_image_data')
                if original_image_data and 'base64,' in original_image_data:
                    import base64
                    from django.core.files.base import ContentFile
                    import uuid

                    # Base64'ü decode et
                    format, imgstr = original_image_data.split(';base64,')
                    ext = format.split('/')[-1]

                    # Dosya oluştur
                    original_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'original_{uuid.uuid4()}.{ext}'
                    )

                    # ✅ DOĞRU YÖNTEM: Doğrudan assign
                    product.image = original_file
                    original_saved = True

                # ✅ Görsel kaydedildiyse tekrar save et
                if cropped_saved or original_saved:
                    product.save()


                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Ürün "{product.name}" başarıyla eklendi.',
                        'item_id': product.id,
                        'redirect_url': reverse('dashboard:products_list')
                    })
                else:
                    messages.success(request, 'Ürün başarıyla eklendi.')
                    return redirect('dashboard:dashboard_products')
                    
            except Exception as e:
                import traceback
                traceback.print_exc()  # Debug için
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Kaydetme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Kaydetme hatası: {str(e)}')
       
        else:
            # Form geçersiz - AJAX ve normal request için hata handling
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
            else:
                # Çeviri hatalarını göster
                for field, errors in form.errors.items():
                    if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                        for error in errors:
                            lang_code = field.split('_')[-1]
                            lang_name = {
                                'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                                'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                            }.get(lang_code, lang_code.upper())
                            field_name = field.replace(f'_{lang_code}', '')
                            messages.error(request, f'{field_name.title()} {lang_name} çevirisi zorunludur.')
                    else:
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
    
    # GET request - redirect to list
    return redirect('dashboard:dashboard_products')

@staff_member_required(login_url='dashboard:dashboard_login')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # ... çeviri ayarları ...
    
    if request.method == 'POST':
        form = ProductFormWithTranslation(
            request.POST, 
            request.FILES, 
            instance=product,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        if form.is_valid():
            try:
                # ✅ DÜZELTME: Önce form'u commit=True ile kaydet
                product = form.save(commit=True)
                
                # ✅ Product None kontrolü
                if product is None:
                    raise ValueError("Form save işlemi başarısız oldu")

                # ✅ KIRPILMIŞ GÖRSELİ KAYDET (Form'dan gelir)
                cropped_saved = False
                if 'image' in request.FILES:
                    product.cropped_image = request.FILES['image']
                    cropped_saved = True

                # ✅ ORİJİNAL GÖRSELİ KAYDET (Base64'ten)
                original_saved = False
                original_image_data = request.POST.get('original_image_data')
                if original_image_data and 'base64,' in original_image_data:
                    import base64
                    from django.core.files.base import ContentFile
                    import uuid

                    # Base64'ü decode et
                    format, imgstr = original_image_data.split(';base64,')
                    ext = format.split('/')[-1]

                    # Dosya oluştur
                    original_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'original_{uuid.uuid4()}.{ext}'
                    )

                    # ✅ DOĞRU YÖNTEM: Doğrudan assign
                    product.image = original_file
                    original_saved = True

                # ✅ Görsel kaydedildiyse tekrar save et
                if cropped_saved or original_saved:
                    product.save()

                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Ürün "{product.name}" başarıyla güncellendi.',
                        'item_id': product.id,
                    })
                else:
                    messages.success(request, 'Ürün başarıyla güncellendi.')
                    return redirect('dashboard:dashboard_products')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Güncelleme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Güncelleme hatası: {str(e)}')
        else:
            # Form geçersiz - AJAX ve normal request için hata handling
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
            else:
                # Çeviri hatalarını göster
                for field, errors in form.errors.items():
                    if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                        for error in errors:
                            lang_code = field.split('_')[-1]
                            lang_name = {
                                'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                                'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                            }.get(lang_code, lang_code.upper())
                            field_name = field.replace(f'_{lang_code}', '')
                            messages.error(request, f'{field_name.title()} {lang_name} çevirisi zorunludur.')
                    else:
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                            
                messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
    
    # GET request - redirect to list (modal'da açılıyor)
    return redirect('dashboard:dashboard_products')

@staff_member_required(login_url='dashboard:dashboard_login')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Görsel varsa sil
                if product.image:
                    try:
                        import os
                        if os.path.isfile(product.image.path):
                            os.remove(product.image.path)
                    except:
                        pass
                
                product.delete()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'"{product_name}" ürünü başarıyla silindi.'
                    })
                else:
                    messages.success(request, f'"{product_name}" ürünü başarıyla silindi.')
                    
        except Exception as e:
            error_message = f'Silme işlemi sırasında hata oluştu: {str(e)}'
            
            # AJAX isteği için JSON hata response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(request, error_message)
    
    return redirect('dashboard:dashboard_products')
# Carousel Yönetimi
@staff_member_required(login_url='dashboard:dashboard_login')
def carousel_list(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    slides = CarouselSlide.objects.all().order_by('order')
    form = CarouselSlideFormWithTranslation(
        translation_enabled=translation_enabled,
        enabled_languages=enabled_languages,
        user=request.user
    )
    
    # ✅ HER DİL İÇİN DEĞERLERI SLIDE OBJESİNE EKLE
    slides_with_translations = []
    for slide in slides:
        # Çeviri değerlerini slide objesine ekle (template erişimi için)
        for lang in enabled_languages:
            if lang != 'tr':
                # Database'den değerleri al ve slide objesine ekle
                title_value = getattr(slide, f'title_{lang}', '') or ''
                desc_value = getattr(slide, f'description_{lang}', '') or ''
                alt_text_value = getattr(slide, f'alt_text_{lang}', '') or ''
                button_text_value = getattr(slide, f'button_text_{lang}', '') or ''
                
                # Slide objesine ekle (her dil için)
                setattr(slide, f'title_{lang}_value', title_value)
                setattr(slide, f'description_{lang}_value', desc_value)
                setattr(slide, f'alt_text_{lang}_value', alt_text_value)
                setattr(slide, f'button_text_{lang}_value', button_text_value)
        
        slide_data = {
            'object': slide,
            'translations': {}  # Artık gerek yok
        }
        slides_with_translations.append(slide_data)
    
    # İstatistikler
    total_slides = slides.count()
    active_slides_count = slides.filter(is_active=True).count()
    
    context = {
        'slides': slides,
        'slides_with_translations': slides_with_translations,
        'form': form,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        'carousel_stats': [
            {'value': total_slides, 'label': 'Toplam Slayt', 'icon': 'fas fa-images', 'color': 'primary'},
            {'value': active_slides_count, 'label': 'Aktif Slaytlar', 'icon': 'fas fa-check-circle', 'color': 'success'},
        ],
        'active_slides_count': active_slides_count,
    }
    return render(request, 'dashboard/carousel/list.html', context)


@staff_member_required(login_url='dashboard:dashboard_login')
def carousel_add(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        print("=== CAROUSEL ADD POST İSTEĞİ ===")
        print(f"POST verileri: {dict(request.POST)}")
        print(f"Dosyalar: {dict(request.FILES)}")
        
        form = CarouselSlideFormWithTranslation(
            request.POST,
            request.FILES,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        if form.is_valid():
            try:
                slide = form.save()
                print(f"✅ CAROUSEL SLIDE BAŞARIYLA KAYDEDİLDİ! ID: {slide.id}, Title: {slide.title}")
                
                # AJAX request için JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Slayt "{slide.title}" başarıyla eklendi.',
                        'slide_id': slide.id,
                        'redirect_url': reverse('dashboard:dashboard_carousel')
                    })
                else:
                    messages.success(request, f'Slayt "{slide.title}" başarıyla eklendi.')
                    return redirect('dashboard:dashboard_carousel')
                    
            except Exception as e:
                print(f"❌ Kaydetme hatası: {str(e)}")
                import traceback
                traceback.print_exc()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Kaydetme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Kaydetme hatası: {str(e)}')
        else:
            print("❌ Form geçersiz!")
            print(f"Hatalar: {dict(form.errors)}")
            
            # Form hatalarını handle et
            error_messages = []
            for field, errors in form.errors.items():
                if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                    lang_code = field.split('_')[-1]
                    lang_name = {
                        'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                        'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                    }.get(lang_code, lang_code.upper())
                    for error in errors:
                        error_msg = f'{field.replace(f"_{lang_code}", "").title()} {lang_name} çevirisi zorunludur.'
                        messages.error(request, error_msg)
                        error_messages.append(error_msg)
                else:
                    for error in errors:
                        error_msg = f'{field}: {error}'
                        messages.error(request, error_msg)
                        error_messages.append(error_msg)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Form hatası',
                    'errors': dict(form.errors),
                    'error_messages': error_messages
                })
    
    # GET request - redirect to carousel list
    return redirect('dashboard:dashboard_carousel')

@staff_member_required(login_url='dashboard:dashboard_login')
def carousel_edit(request, pk):
    slide = get_object_or_404(CarouselSlide, pk=pk)
    
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        print("=== CAROUSEL EDIT POST İSTEĞİ ===")
        print(f"POST verileri: {dict(request.POST)}")
        
        form = CarouselSlideFormWithTranslation(
            request.POST, 
            request.FILES, 
            instance=slide,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        if form.is_valid():
            try:
                slide = form.save()
                print(f"✅ CAROUSEL SLIDE BAŞARIYLA GÜNCELLENDİ! ID: {slide.id}")
                
                # AJAX request için JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Slayt "{slide.title}" başarıyla güncellendi.',
                        'slide_id': slide.id,
                    })
                else:
                    messages.success(request, f'Slayt "{slide.title}" başarıyla güncellendi.')
                    return redirect('dashboard:dashboard_carousel')
                    
            except Exception as e:
                print(f"❌ Güncelleme hatası: {str(e)}")
                import traceback
                traceback.print_exc()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Güncelleme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Güncelleme hatası: {str(e)}')
        else:
            print("❌ Form geçersiz!")
            print(f"Hatalar: {dict(form.errors)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
            else:
                messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
    
    # GET request - redirect to list (modal'da açılıyor)
    return redirect('dashboard:dashboard_carousel')
@staff_member_required(login_url='dashboard:dashboard_login')
def carousel_delete(request, pk):
    slide = get_object_or_404(CarouselSlide, pk=pk)
    slide.delete()
    messages.success(request, 'Slayt silindi.')
    return redirect('dashboard:dashboard_carousel')

# dashboard/views.py (mevcut views'lara ekleyin)

@staff_member_required(login_url='dashboard:dashboard_login')
def review_add(request):
    if request.method == 'POST':
        form = CustomerReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yorum eklendi.')
            return redirect('dashboard:dashboard_messages')
    else:
        form = CustomerReviewForm()
    return render(request, 'dashboard/reviews/add.html', {'form': form})

@staff_member_required(login_url='dashboard:dashboard_login')
def review_edit(request, pk):
    review = get_object_or_404(CustomerReview, pk=pk)
    if request.method == 'POST':
        form = CustomerReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yorum güncellendi.')
            return redirect('dashboard:dashboard_messages')
    else:
        form = CustomerReviewForm(instance=review)
    return render(request, 'dashboard/reviews/edit.html', {'form': form, 'review': review})

@staff_member_required(login_url='dashboard:dashboard_login')
def review_delete(request, pk):
    review = get_object_or_404(CustomerReview, pk=pk)
    review.delete()
    messages.success(request, 'Yorum silindi.')
    return redirect('dashboard:dashboard_messages')


@staff_member_required(login_url='dashboard:dashboard_login')
def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    form = ProductForm()  # Yeni ürün eklemek için boş form
    
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'form': form
    }
    return render(request, 'dashboard/categories/products_list.html', context)




# Hizmet views
# dashboard/views.py - Service views kısmını şu şekilde değiştirin:



logger = logging.getLogger(__name__)

# dashboard/views.py - service_list fonksiyonunu tamamen değiştirin:

@staff_member_required(login_url='dashboard:dashboard_login')
@never_cache
def service_list(request):
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    # Çeviri sistemi kontrol et
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    # Hizmetleri getir
    services = Service.objects.all().order_by('order')
    
    # Her service için çeviri verilerini yükle
    services_with_translations = []
    for service in services:
        service_data = {
            'object': service,
            'translations': {}
        }
        
        # Her dil için çeviri verilerini al
        for lang in enabled_languages:
            if lang != 'tr':
                title_value = getattr(service, f'title_{lang}', '') or ''
                desc_value = getattr(service, f'description_{lang}', '') or ''
                
                # Service objesine ekle (template erişimi için)
                setattr(service, f'title_{lang}', title_value)
                setattr(service, f'description_{lang}', desc_value)
                
                service_data['translations'][lang] = {
                    'title': title_value,
                    'description': desc_value,
                }
        
        services_with_translations.append(service_data)
    
    # Diğer kısımlar aynı kalacak...
    total_services = services.count()
    active_services = services.filter(is_active=True).count()
    inactive_services = services.filter(is_active=False).count()
    
    services_table_config = {
        'title': 'Hizmet Listesi',
        'icon': 'fas fa-list',
        'search_placeholder': 'Hizmet ara...',
        'search_id': 'serviceSearch',
        'table_id': 'servicesTable',
        'model_name': 'Service',
        'model_name_lower': 'service',
        'add_button_text': 'Yeni Hizmet Ekle',
        'empty_icon': 'fas fa-cogs',
        'empty_title': 'Henüz hizmet eklenmemiş',
        'empty_message': 'İlk hizmetinizi ekleyerek başlayın',
        'empty_action_attrs': 'data-bs-toggle="modal" data-bs-target="#addServiceModal"'
    }
    
    services_table_headers = [
        {'title': 'ID', 'width': '60px', 'class': 'text-center'},
        {'title': 'Sıralama', 'width': '80px', 'class': 'text-center'},
        {'title': 'Görsel', 'width': '80px', 'class': 'text-center'},
        {'title': 'Hizmet', 'icon': 'fas fa-heading'},
        {'title': 'Durum', 'width': '120px', 'class': 'text-center'},
        {'title': 'İşlemler', 'width': '150px', 'class': 'text-center'},
    ]
    
    services_modal_config = {
        'model_name': 'Service',
        'model_name_lower': 'service',
        'add_title': 'Yeni Hizmet Ekle',
        'edit_title': 'Hizmet Düzenle',
        'view_title': 'Hizmet Detayları',
        'save_text': 'Hizmeti Kaydet',
        'item_type': 'hizmet',
        'delete_warning': 'Bu hizmet kalıcı olarak silinecek!',
        'add_url': reverse('dashboard:service_create'),
        'edit_url_pattern': '/dashboard/services/edit/',
        'size': 'modal-xl',
        'view_size': 'modal-lg'
    }

    context = {
        'services': services,
        'total_services': total_services,
        'active_services': active_services,
        'inactive_services': inactive_services,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        'services_table_config': services_table_config,
        'services_table_headers': services_table_headers,
        'services_modal_config': services_modal_config,
        'services_with_translations': services_with_translations,
    }
    return render(request, 'dashboard/services/list.html', context)


@staff_member_required(login_url='dashboard:dashboard_login')
def service_create(request):
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        print("=== SERVICE CREATE POST İSTEĞİ ===")
        print(f"POST verileri: {dict(request.POST)}")
        
        form = ServiceFormWithTranslation(
            request.POST, 
            request.FILES,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        if form.is_valid():
            try:
                service = form.save()
                print(f"✅ HİZMET BAŞARIYLA KAYDEDİLDİ! ID: {service.id}, Title: {service.title}")
                
                # AJAX request için JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Hizmet "{service.title}" başarıyla eklendi.',
                        'service_id': service.id,
                        'redirect_url': reverse('dashboard:service_list')
                    })
                else:
                    messages.success(request, f'Hizmet "{service.title}" başarıyla eklendi.')
                    return redirect('dashboard:service_list')
                    
            except Exception as e:
                print(f"❌ Kaydetme hatası: {str(e)}")
                import traceback
                traceback.print_exc()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Kaydetme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Kaydetme hatası: {str(e)}')
        else:
            print("❌ Form geçersiz!")
            print(f"Hatalar: {dict(form.errors)}")
            
            # Çeviri hatalarını handle et
            translation_errors = []
            for field, errors in form.errors.items():
                if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                    lang_code = field.split('_')[-1]
                    lang_name = {
                        'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                        'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                    }.get(lang_code, lang_code.upper())
                    for error in errors:
                        messages.error(request, f'{field.replace(f"_{lang_code}", "").title()} {lang_name} çevirisi zorunludur.')
                else:
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
    
    # GET request - redirect to list
    return redirect('dashboard:service_list')


@staff_member_required(login_url='dashboard:dashboard_login')
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        form = ServiceFormWithTranslation(
            request.POST, 
            request.FILES, 
            instance=service,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        if form.is_valid():
            try:
                service = form.save()
                
                # AJAX request için JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Hizmet "{service.title}" başarıyla güncellendi.',
                        'service_id': service.id,
                    })
                else:
                    messages.success(request, f'Hizmet "{service.title}" başarıyla güncellendi.')
                    return redirect('dashboard:service_list')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Güncelleme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Güncelleme hatası: {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors),
                })
            else:
                messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
    
    # GET request - redirect to list (modal'da açılıyor)
    print(f"DEBUG: Service ID: {service.id}")
    print(f"DEBUG: Title: {service.title}")  
    print(f"DEBUG: Title_en: {getattr(service, 'title_en', 'BULUNAMADI')}")
    print(f"DEBUG: Description_en: {getattr(service, 'description_en', 'BULUNAMADI')}")
    return redirect('dashboard:service_list')

@staff_member_required(login_url='dashboard:dashboard_login')
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service_title = service.title
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                service.delete()
                
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Hizmet "{service_title}" başarıyla silindi.'
                    })
                else:
                    messages.success(request, f'Hizmet "{service_title}" başarıyla silindi.')
                    
        except Exception as e:
            error_message = f'Silme işlemi sırasında hata oluştu: {str(e)}'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(request, error_message)
    
    return redirect('dashboard:service_list')




@staff_member_required(login_url='dashboard:dashboard_login')
def service_status_toggle(request, pk):
    """Hizmetin aktif/pasif durumunu AJAX ile değiştir"""
    if request.method == 'POST':
        service = get_object_or_404(Service, pk=pk)
        
        try:
            # Durumu değiştir
            service.is_active = not service.is_active
            service.save()
            
            return JsonResponse({
                'success': True,
                'is_active': service.is_active,
                'status_text': 'Aktif' if service.is_active else 'Pasif',
                'status_color': 'success' if service.is_active else 'danger',
                'message': f'"{service.title}" durumu güncellendi.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Hata oluştu: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'})

@staff_member_required(login_url='dashboard:dashboard_login')
def service_footer_toggle(request, pk):
    """Hizmetin footer durumunu AJAX ile değiştir"""
    if request.method == 'POST':
        service = get_object_or_404(Service, pk=pk)
        
        try:
            # Footer'da maksimum 6 hizmet kontrolü
            if not service.is_footer:
                footer_services_count = Service.objects.filter(is_footer=True, is_active=True).count()
                if footer_services_count >= 6:
                    return JsonResponse({
                        'success': False,
                        'error': 'Footer\'da maksimum 6 hizmet gösterilebilir.'
                    })
            
            # Durumu değiştir
            service.is_footer = not service.is_footer
            service.save()
            
            # Güncel footer hizmet sayısını hesapla
            footer_count = Service.objects.filter(is_footer=True, is_active=True).count()
            
            return JsonResponse({
                'success': True,
                'is_footer': service.is_footer,
                'footer_count': footer_count,
                'message': f'"{service.title}" footer durumu güncellendi.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Hata oluştu: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'})


# Ekip views
@staff_member_required(login_url='dashboard:dashboard_login')
def team_member_list(request):
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    from django.db.models import Count, Avg
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()
    
    team_members = TeamMember.objects.all().order_by('order')
    
    # ✅ İSTATİSTİKLERİ HESAPLA
    total_members = team_members.count()
    active_members = team_members.filter(is_active=True).count()
    
    # Pozisyon sayısı (unique pozisyonlar)
    positions_count = team_members.values('position').distinct().count()
    
    # Ortalama sıralama
    avg_order_result = team_members.aggregate(avg_order=Avg('order'))
    avg_order = round(avg_order_result['avg_order'] or 0, 1)
    
    team_members_with_translations = []
    for member in team_members:
        member_data = {
            'object': member,
            'translations': {}
        }
        
        for lang in enabled_languages:
            if lang != 'tr':
                member_data['translations'][lang] = {
                    'name': getattr(member, f'name_{lang}', ''),
                    'position': getattr(member, f'position_{lang}', ''),
                    'bio': getattr(member, f'bio_{lang}', ''),
                }
        
        team_members_with_translations.append(member_data)
    
    context = {
        'team_members': team_members,
        'team_members_with_translations': team_members_with_translations,
        'translation_enabled': translation_enabled,
        'enabled_languages': enabled_languages,
        # ✅ İSTATİSTİKLER EKLENDİ
        'total_members': total_members,
        'active_members': active_members,
        'positions_count': positions_count,
        'avg_order': avg_order,
    }
    return render(request, 'dashboard/team/list.html', context)

@staff_member_required(login_url='dashboard:dashboard_login')
def team_member_create(request):
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        form = TeamMemberFormWithTranslation(
            request.POST, 
            request.FILES,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        if form.is_valid():
            try:
                team_member = form.save()
                
                # ★ AJAX İSTEĞİ İÇİN JSON RESPONSE DÖNDÜR
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Ekip üyesi "{team_member.name}" başarıyla eklendi.',
                        'member_id': team_member.id,
                    })
                else:
                    messages.success(request, 'Ekip üyesi başarıyla eklendi.')
                    return redirect('dashboard:team_member_list')
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Kaydetme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Kaydetme hatası: {str(e)}')
        else:
            # Form geçersiz - AJAX için hata response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Form hatası! Lütfen alanları kontrol edin.',
                    'errors': dict(form.errors),
                })
            else:
                # Çeviri hatalarını göster
                for field, errors in form.errors.items():
                    if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                        for error in errors:
                            lang_code = field.split('_')[-1]
                            lang_name = {
                                'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                                'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                            }.get(lang_code, lang_code.upper())
                            field_name = field.replace(f'_{lang_code}', '')
                            messages.error(request, f'{field_name.title()} {lang_name} çevirisi zorunludur.')
                    else:
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
    
    # GET request - redirect to list
    return redirect('dashboard:team_member_list')

@staff_member_required(login_url='dashboard:dashboard_login')
def team_member_edit(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    
    # Çeviri sistemi kontrol et
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    
    site_settings = SiteSettings.get_current()
    translation_enabled = site_settings.translation_enabled
    
    enabled_languages = ['tr']
    if translation_enabled and request.user.is_authenticated:
        user_translation_settings, created = DashboardTranslationSettings.objects.get_or_create(
            user=request.user,
            defaults={'enabled_languages': ['tr']}
        )
        enabled_languages = user_translation_settings.get_all_languages()

    if request.method == 'POST':
        print("=== TEAM MEMBER EDIT DEBUG ===")
        print(f"POST verileri: {dict(request.POST)}")
        print(f"Dosyalar: {dict(request.FILES)}")
        print(f"Translation enabled: {translation_enabled}")
        print(f"Enabled languages: {enabled_languages}")
        
        form = TeamMemberFormWithTranslation(
            request.POST, 
            request.FILES, 
            instance=team_member,
            translation_enabled=translation_enabled,
            enabled_languages=enabled_languages,
            user=request.user
        )
        
        print(f"Form oluşturuldu. Form fields: {list(form.fields.keys())}")
        
        if form.is_valid():
            print("✅ Form geçerli!")
            print(f"Cleaned data: {form.cleaned_data}")
            try:
                team_member = form.save()
                print(f"✅ SAVE başarılı! ID: {team_member.id}")
                print(f"Name: {team_member.name}, Position: {team_member.position}")
                
                # AJAX response için
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Ekip üyesi "{team_member.name}" başarıyla güncellendi.',
                        'member_id': team_member.id,
                    })
                else:
                    messages.success(request, 'Ekip üyesi başarıyla güncellendi.')
                    return redirect('dashboard:team_member_list')
                    
            except Exception as e:
                print(f"❌ SAVE hatası: {str(e)}")
                import traceback
                traceback.print_exc()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Güncelleme hatası: {str(e)}'
                    })
                else:
                    messages.error(request, f'Güncelleme hatası: {str(e)}')
        else:
            print("❌ Form geçersiz!")
            print(f"Form errors: {dict(form.errors)}")
            
            # Form geçersiz - AJAX için hata response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Form hatası! Lütfen alanları kontrol edin.',
                    'errors': dict(form.errors),
                })
            else:
                # Çeviri hatalarını göster
                for field, errors in form.errors.items():
                    if '_en' in field or '_de' in field or '_fr' in field or '_es' in field or '_ru' in field or '_ar' in field:
                        for error in errors:
                            lang_code = field.split('_')[-1]
                            lang_name = {
                                'en': 'İngilizce', 'de': 'Almanca', 'fr': 'Fransızca',
                                'es': 'İspanyolca', 'ru': 'Rusça', 'ar': 'Arapça'
                            }.get(lang_code, lang_code.upper())
                            field_name = field.replace(f'_{lang_code}', '')
                            messages.error(request, f'{field_name.title()} {lang_name} çevirisi zorunludur.')
                    else:
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                            
                messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
    
    # GET request - redirect to list
    return redirect('dashboard:team_member_list')



@staff_member_required(login_url='dashboard:dashboard_login')
def team_member_delete(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    team_member_name = team_member.name
    if request.method == 'POST':
        with transaction.atomic():
            team_member.delete()
            messages.success(request, f'Ekip üyesi "{team_member_name}" başarıyla silindi.')
    return redirect('dashboard:team_member_list')

class DashboardLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('dashboard:dashboard_login')
    
    def post(self, request):
        logout(request)
        return redirect('dashboard:dashboard_login')


 


@staff_member_required(login_url='dashboard:dashboard_login')
def review_list(request):
    # Pagination eklemek için
    page = request.GET.get('page', 1)
    reviews_list = Review.objects.all().order_by('-created_at')
    paginator = Paginator(reviews_list, 10)  # Her sayfada 10 yorum
    
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/reviews/list.html', {'reviews': reviews})




@staff_member_required(login_url='dashboard:dashboard_login')
def review_status_toggle(request, id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=id)
        review.is_approved = not review.is_approved
        review.save()
        status = "onaylandı" if review.is_approved else "onayı kaldırıldı"
        messages.success(request, f'Yorum başarıyla {status}.')
        return redirect('dashboard:reviews')
    return redirect('dashboard:reviews')

@staff_member_required(login_url='dashboard:dashboard_login')
def review_delete(request, id):
    review = get_object_or_404(Review, id=id)
    review.delete()
    messages.success(request, 'Yorum silindi.')
    return redirect('dashboard:reviews')





# KULLANICI YÖNETİMİ VIEWS

@staff_member_required(login_url='dashboard:dashboard_login')
def users_list(request):
    """Kullanıcı listesi görüntüleme"""
    users = User.objects.all().order_by('username')
    
    # Filtreleme
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'staff':
        users = users.filter(is_staff=True)
    
    if search:
        users = users.filter(
            models.Q(username__icontains=search) |
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
    }
    return render(request, 'dashboard/users/list.html', context)

@staff_member_required(login_url='dashboard:dashboard_login')
def user_create(request):
    """Yeni kullanıcı oluşturma"""
    if not request.user.is_superuser:
        messages.error(request, 'Bu işlem için süper kullanıcı yetkisi gereklidir.')
        return redirect('dashboard:users_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Kullanıcı "{user.username}" başarıyla oluşturuldu.')
                return redirect('dashboard:users_list')
            except Exception as e:
                messages.error(request, f'Kullanıcı oluşturulurken hata oluştu: {str(e)}')
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'dashboard/users/form.html', {
        'form': form,
        'title': 'Yeni Kullanıcı Oluştur',
        'action': 'create'
    })

@staff_member_required(login_url='dashboard:dashboard_login')
def user_edit(request, user_id):
    """Kullanıcı düzenleme"""
    if not request.user.is_superuser:
        messages.error(request, 'Bu işlem için süper kullanıcı yetkisi gereklidir.')
        return redirect('dashboard:users_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # Süper kullanıcıların birbirini düzenlemesini engelle
    if user.is_superuser and request.user != user:
        messages.error(request, 'Başka süper kullanıcıları düzenleyemezsiniz.')
        return redirect('dashboard:users_list')
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Kullanıcı "{user.username}" başarıyla güncellendi.')
                return redirect('dashboard:users_list')
            except Exception as e:
                messages.error(request, f'Kullanıcı güncellenirken hata oluştu: {str(e)}')
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'dashboard/users/form.html', {
        'form': form,
        'title': f'Kullanıcı Düzenle: {user.username}',
        'action': 'edit',
        'edit_user': user
    })

@staff_member_required(login_url='dashboard:dashboard_login')
def user_delete(request, user_id):
    """Kullanıcı silme"""
    if not request.user.is_superuser:
        messages.error(request, 'Bu işlem için süper kullanıcı yetkisi gereklidir.')
        return redirect('dashboard:users_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # Kendini ve diğer süper kullanıcıları silmeyi engelle
    if user.is_superuser:
        messages.error(request, 'Süper kullanıcılar silinemez.')
        return redirect('dashboard:users_list')
    
    if user == request.user:
        messages.error(request, 'Kendi hesabınızı silemezsiniz.')
        return redirect('dashboard:users_list')
    
    if request.method == 'POST':
        username = user.username
        try:
            user.delete()
            messages.success(request, f'Kullanıcı "{username}" başarıyla silindi.')
        except Exception as e:
            messages.error(request, f'Kullanıcı silinirken hata oluştu: {str(e)}')
    
    return redirect('dashboard:users_list')

@staff_member_required(login_url='dashboard:dashboard_login')
def user_password_change(request, user_id):
    """Kullanıcı şifre değiştirme"""
    if not request.user.is_superuser:
        messages.error(request, 'Bu işlem için süper kullanıcı yetkisi gereklidir.')
        return redirect('dashboard:users_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # Süper kullanıcıların birbirinin şifresini değiştirmesini engelle
    if user.is_superuser and request.user != user:
        messages.error(request, 'Başka süper kullanıcıların şifresini değiştiremezsiniz.')
        return redirect('dashboard:users_list')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not new_password or len(new_password) < 8:
            messages.error(request, 'Şifre en az 8 karakter olmalıdır.')
        elif new_password != confirm_password:
            messages.error(request, 'Şifreler eşleşmiyor.')
        else:
            try:
                user.set_password(new_password)
                user.save()
                
                # Eğer kendi şifresini değiştiriyorsa session'ı güncelle
                if user == request.user:
                    update_session_auth_hash(request, user)
                
                messages.success(request, f'"{user.username}" kullanıcısının şifresi başarıyla değiştirildi.')
                return redirect('dashboard:users_list')
            except Exception as e:
                messages.error(request, f'Şifre değiştirilemedi: {str(e)}')
    
    return render(request, 'dashboard/users/password_change.html', {
        'edit_user': user,
        'title': f'Şifre Değiştir: {user.username}'
    })

@staff_member_required(login_url='dashboard:dashboard_login')
def user_toggle_status(request, user_id):
    """Kullanıcı aktif/pasif durumu değiştirme"""
    if not request.user.is_superuser:
        messages.error(request, 'Bu işlem için süper kullanıcı yetkisi gereklidir.')
        return redirect('dashboard:users_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # Süper kullanıcıları pasif yapma
    if user.is_superuser:
        messages.error(request, 'Süper kullanıcıların durumu değiştirilemez.')
        return redirect('dashboard:users_list')
    
    # Kendini pasif yapma
    if user == request.user:
        messages.error(request, 'Kendi durumunuzu değiştiremezsiniz.')
        return redirect('dashboard:users_list')
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status = "aktif" if user.is_active else "pasif"
        messages.success(request, f'Kullanıcı "{user.username}" {status} duruma getirildi.')
    
    return redirect('dashboard:users_list')


@staff_member_required(login_url='dashboard:dashboard_login')
def activities_list(request):
    from django.utils import timezone
    from datetime import datetime, timedelta
    import json
    
    # Filtreleme parametreleri
    days = int(request.GET.get('days', 30))  # Son kaç gün
    activity_type = request.GET.get('type', 'all')  # Aktivite türü
    
    # Tarih aralığı
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Tüm aktiviteleri topla
    all_activities = []
    
    # Ürün aktiviteleri
    if activity_type in ['all', 'products']:
        products = Product.objects.filter(created_at__gte=start_date).order_by('-created_at')
        for product in products:
            all_activities.append({
                'type': 'product_added',
                'title': f'Yeni ürün eklendi: {product.name}',
                'description': f'{product.category.name} kategorisine eklendi',
                'time': product.created_at,
                'icon': 'fas fa-plus',
                'color': 'primary',
                'model': 'Product',
                'object_id': product.id
            })
    
    # Yorum aktiviteleri
    if activity_type in ['all', 'reviews']:
        reviews = Review.objects.filter(created_at__gte=start_date).order_by('-created_at')
        for review in reviews:
            all_activities.append({
                'type': 'review_added',
                'title': f'{review.rating} yıldızlı yorum alındı',
                'description': f'{review.name} tarafından',
                'time': review.created_at,
                'icon': 'fas fa-star',
                'color': 'success' if review.is_approved else 'warning',
                'model': 'Review',
                'object_id': review.id
            })
    
    # Mesaj aktiviteleri
    if activity_type in ['all', 'messages']:
        messages = Contact.objects.filter(created_at__gte=start_date).order_by('-created_at')
        for message in messages:
            all_activities.append({
                'type': 'message_received',
                'title': f'Yeni mesaj: {message.subject}',
                'description': f'{message.name} tarafından gönderildi',
                'time': message.created_at,
                'icon': 'fas fa-envelope',
                'color': 'info' if message.is_read else 'danger',
                'model': 'Contact',
                'object_id': message.id
            })
    
    # Kategori aktiviteleri
    if activity_type in ['all', 'categories']:
        categories = Category.objects.filter(created_at__gte=start_date).order_by('-created_at')
        for category in categories:
            all_activities.append({
                'type': 'category_added',
                'title': f'Yeni kategori eklendi: {category.name}',
                'description': f'Toplam {category.product_set.count()} ürün içeriyor',
                'time': category.created_at,
                'icon': 'fas fa-tags',
                'color': 'info',
                'model': 'Category',
                'object_id': category.id
            })
    
    # Aktiviteleri tarihe göre sırala
    all_activities.sort(key=lambda x: x['time'], reverse=True)
    
    # Sayfalama
    paginator = Paginator(all_activities, 20)
    page = request.GET.get('page')
    try:
        activities = paginator.page(page)
    except PageNotAnInteger:
        activities = paginator.page(1)
    except EmptyPage:
        activities = paginator.page(paginator.num_pages)
    
    context = {
        'activities': activities,
        'total_activities': len(all_activities),
        'days': days,
        'activity_type': activity_type,
        'activity_types': [
            ('all', 'Tüm Aktiviteler'),
            ('products', 'Ürün Aktiviteleri'),
            ('reviews', 'Yorum Aktiviteleri'),
            ('messages', 'Mesaj Aktiviteleri'),
            ('categories', 'Kategori Aktiviteleri'),
        ]
    }
    
    return render(request, 'dashboard/activities/list.html', context)


#Bildirim

@staff_member_required(login_url='dashboard:dashboard_login')
def get_notifications(request):
    """Bildirimleri JSON olarak döndür"""
    notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(is_read=False).count()
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime('%d.%m.%Y %H:%M'),
            'redirect_url': notification.redirect_url,
            'time_ago': notification.created_at
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count,
        'has_notifications': unread_count > 0
    })

@staff_member_required(login_url='dashboard:dashboard_login')
def mark_notification_read(request, notification_id):
    """Bildirimi okundu olarak işaretle"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, is_read=False)
            notification.is_read = True
            notification.save()
            
            return JsonResponse({
                'success': True,
                'redirect_url': notification.redirect_url
            })
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bildirim bulunamadı'})
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'})

@staff_member_required(login_url='dashboard:dashboard_login')
def mark_all_notifications_read(request):
    """Tüm bildirimleri okundu olarak işaretle"""
    if request.method == 'POST':
        count = Notification.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({
            'success': True,
            'marked_count': count
        })
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'})

@staff_member_required(login_url='dashboard:dashboard_login')
def notification_popup_content(request):
    """Bildirim popup içeriğini döndür"""
    notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:10]
    
    html = render_to_string('dashboard/notifications/popup_content.html', {
        'notifications': notifications
    })
    
    return JsonResponse({
        'html': html,
        'unread_count': Notification.objects.filter(is_read=False).count()
    })
    
    
# dashboard/views.py - eklenecek kısım
@staff_member_required(login_url='dashboard:dashboard_login')
def notifications_list(request):
    """Bildirimler listesi sayfası"""
    notifications = Notification.objects.all().order_by('-created_at')
    
    # Filtreleme
    notification_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    try:
        notifications = paginator.page(page)
    except:
        notifications = paginator.page(1)
    
    context = {
        'notifications': notifications,
        'notification_types': Notification.NOTIFICATION_TYPES,
        'current_type': notification_type,
        'current_status': status,
        'unread_count': Notification.objects.filter(is_read=False).count(),
    }
    
    return render(request, 'dashboard/notifications/list.html', context)

# dashboard/views.py - eklenecek kısım
@staff_member_required(login_url='dashboard:dashboard_login')
def delete_notification(request, notification_id):
    """Bildirimi sil"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Bildirim bulunamadı'})
    
    return JsonResponse({'success': False, 'error': 'Geçersiz istek'})





@staff_member_required(login_url='dashboard:dashboard_login')
def translation_settings(request):
    """Çeviri ayarları sayfası"""
    from core.models import SiteSettings
    from .models import DashboardTranslationSettings
    from .forms import DashboardTranslationSettingsForm 
    from django.conf import settings
    from django.http import JsonResponse
    from django.utils import translation
    
    # Çeviri sistemi aktif mi kontrol et
    site_settings = SiteSettings.get_current()
    if not site_settings.translation_enabled:
        messages.error(request, 'Çeviri sistemi aktif değil.')
        return redirect('dashboard:home')
    
    # Kullanıcının çeviri ayarlarını al/oluştur
    user_settings, created = DashboardTranslationSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'enabled_languages': [],
            'dashboard_language': 'tr',
            'primary_language': 'tr'
        }
    )
    
    if request.method == 'POST':
        print(f"[VIEW] POST verileri: {dict(request.POST)}")
        
        # Ana dil güncellemesi
        primary_language = request.POST.get('primary_language', user_settings.primary_language)
        
        # Dashboard dili güncellemesi
        dashboard_language = request.POST.get('dashboard_language', user_settings.dashboard_language)
        
        # Ek diller güncellemesi
        enabled_languages = request.POST.getlist('enabled_languages')
        print(f"[DEBUG] Alınan ek diller: {enabled_languages}")
        
        # Ana dili de dahil et (her zaman)
        if primary_language not in enabled_languages:
            enabled_languages.append(primary_language)
        
        print(f"[DEBUG] Kaydedilecek tüm diller: {enabled_languages}")
        
        # KAYDET - HER DURUMDA
        user_settings.primary_language = primary_language
        user_settings.dashboard_language = dashboard_language
        user_settings.enabled_languages = enabled_languages
        user_settings.save()
        
        print(f"[VIEW] ✅ BAŞARIYLA KAYDEDİLDİ!")
        print(f"[VIEW] Veritabanı durumu - Primary: {user_settings.primary_language}, Dashboard: {user_settings.dashboard_language}, Enabled: {user_settings.enabled_languages}")
        
        # AJAX isteği kontrolü
        auto_save = request.POST.get('auto_save')
        
        if auto_save == 'primary_language_change':
            return JsonResponse({
                'success': True,
                'message': f'Site ana dili {primary_language.upper()} olarak değiştirildi',
                'primary_language': primary_language,
            })
        elif auto_save == 'dashboard_language_only':
            # Django session'ında dashboard dilini ayarla
            request.session['dashboard_language'] = dashboard_language
            
            response = JsonResponse({
                'success': True,
                'message': f'Dashboard dili {dashboard_language.upper()} olarak değiştirildi',
                'dashboard_language': dashboard_language,
            })
            
            # Cookie da ayarla
            response.set_cookie(
                'dashboard_language',
                dashboard_language,
                max_age=365*24*60*60,  # 1 yıl
                path='/',
                secure=False,  # Development için
                httponly=False,
                samesite='Lax'
            )
            return response
        elif auto_save == 'enabled_languages_only':
            return JsonResponse({
                'success': True,
                'message': f'Ek diller güncellendi: {", ".join(enabled_languages)}',
                'enabled_languages': enabled_languages,
            })
        
        # Normal form submit
        messages.success(request, 'Çeviri ayarları başarıyla güncellendi.')
        return redirect('dashboard:translation_settings')
    
    # Mevcut dil listesi (Ana dil hariç)
    available_languages = []
    all_languages = [
        {'code': 'tr', 'name': 'Türkçe', 'flag_name': '🇹🇷 Türkçe'},
        {'code': 'en', 'name': 'İngilizce', 'flag_name': '🇺🇸 İngilizce'},
        {'code': 'de', 'name': 'Almanca', 'flag_name': '🇩🇪 Almanca'},
        {'code': 'fr', 'name': 'Fransızca', 'flag_name': '🇫🇷 Fransızca'},
        {'code': 'es', 'name': 'İspanyolca', 'flag_name': '🇪🇸 İspanyolca'},
        {'code': 'ru', 'name': 'Rusça', 'flag_name': '🇷🇺 Rusça'},
        {'code': 'ar', 'name': 'Arapça', 'flag_name': '🇸🇦 Arapça'},
    ]
    
    # Ana dil hariç diğer dilleri göster
    for lang in all_languages:
        if lang['code'] != user_settings.primary_language:
            available_languages.append(lang)
    
    dashboard_language_options = [
        {'value': lang['code'], 'label': lang['flag_name']} 
        for lang in all_languages
    ]
    
    # Primary dil seçenekleri oluştur - YENİ EKLENEN  
    primary_language_options = [
        {'value': lang['code'], 'label': f"🌟 {lang['flag_name']}"} 
        for lang in all_languages
    ]
    
    # Veritabanından en güncel verileri al
    user_settings.refresh_from_db()
    
    # CONTEXT'İ ŞUNUNLA DEĞİŞTİR:
    # Form oluştur
    form = DashboardTranslationSettingsForm(instance=user_settings)
    
    # CONTEXT'İ ŞUNUNLA DEĞİŞTİR:
    context = {
        'form': form,  # BU SATIRI EKLE
        'user_settings': user_settings,
        'available_languages': available_languages,
        'dashboard_languages': settings.LANGUAGES,
        'dashboard_language_options': dashboard_language_options,  # YENİ
        'primary_language_options': primary_language_options,      # YENİ
        'translation_enabled': True,
        'enabled_language_codes': user_settings.enabled_languages,
    }
    
    # DEBUG: Context'i kontrol et
    print(f"[CONTEXT] user_settings.enabled_languages: {user_settings.enabled_languages}")
    print(f"[CONTEXT] user_settings.primary_language: {user_settings.primary_language}")
    print(f"[CONTEXT] user_settings.dashboard_language: {user_settings.dashboard_language}")
    print(f"[CONTEXT] available_languages: {[lang['code'] for lang in available_languages]}")
    
    return render(request, 'dashboard/translation/settings.html', context)


     
# PDF Katalog yönetimi için eklenecek kodlar

# dashboard/views.py - Dosyanın sonuna ekleyin

@staff_member_required(login_url='dashboard:dashboard_login')
def pdf_catalog_management(request):
    """PDF Katalog Yönetimi Sayfası"""
    from core.models import SiteSettings
    
    site_settings = SiteSettings.get_current()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_status':
            # Katalog aktif/pasif durumu değiştir
            site_settings.pdf_catalog_enabled = not site_settings.pdf_catalog_enabled
            site_settings.save()
            status = "aktif edildi" if site_settings.pdf_catalog_enabled else "pasif edildi"
            messages.success(request, f'PDF Katalog {status}.')
            
        elif action == 'update_title':
            # Katalog başlığını güncelle
            new_title = request.POST.get('catalog_title', '').strip()
            if new_title:
                site_settings.pdf_catalog_title = new_title
                site_settings.save()
                messages.success(request, 'Katalog başlığı güncellendi.')
            else:
                messages.error(request, 'Katalog başlığı boş olamaz.')
                
        elif action == 'upload_catalog':
            # Yeni PDF dosyası yükle
            if 'catalog_file' in request.FILES:
                # Eski dosyayı sil
                if site_settings.pdf_catalog_file:
                    import os
                    try:
                        if os.path.isfile(site_settings.pdf_catalog_file.path):
                            os.remove(site_settings.pdf_catalog_file.path)
                    except:
                        pass
                
                site_settings.pdf_catalog_file = request.FILES['catalog_file']
                site_settings.save()
                messages.success(request, 'PDF Katalog dosyası başarıyla yüklendi.')
            else:
                messages.error(request, 'Lütfen bir PDF dosyası seçin.')
                
        elif action == 'delete_catalog':
            # PDF dosyasını sil
            if site_settings.pdf_catalog_file:
                import os
                try:
                    if os.path.isfile(site_settings.pdf_catalog_file.path):
                        os.remove(site_settings.pdf_catalog_file.path)
                except:
                    pass
                
                site_settings.pdf_catalog_file = None
                site_settings.pdf_catalog_enabled = False
                site_settings.save()
                messages.success(request, 'PDF Katalog dosyası silindi ve katalog pasif edildi.')
            else:
                messages.warning(request, 'Silinecek katalog dosyası bulunamadı.')
        
        return redirect('dashboard:pdf_catalog_management')
    
    # İstatistikler
    stats = {
        'is_enabled': site_settings.pdf_catalog_enabled,
        'has_file': bool(site_settings.pdf_catalog_file),
        'title': site_settings.pdf_catalog_title,
        'file_size': None,
        'file_size_kb': None,
        'file_size_mb': None,
        'file_size_display': None,
        'upload_date': None,
    }
    
    if site_settings.pdf_catalog_file:
        try:
            import os
            file_size_bytes = os.path.getsize(site_settings.pdf_catalog_file.path)
            stats['file_size'] = file_size_bytes
            stats['upload_date'] = site_settings.updated_at
            
            # Dosya boyutu hesaplamaları
            if file_size_bytes < 1024:
                stats['file_size_display'] = f"{file_size_bytes} B"
            elif file_size_bytes < 1048576:  # 1MB
                stats['file_size_kb'] = round(file_size_bytes / 1024, 1)
                stats['file_size_display'] = f"{stats['file_size_kb']} KB"
            else:  # 1MB ve üzeri
                stats['file_size_mb'] = round(file_size_bytes / 1048576, 2)
                stats['file_size_display'] = f"{stats['file_size_mb']} MB"
                
        except Exception as e:
            print(f"Dosya boyutu hesaplama hatası: {e}")
            pass
    
    context = {
        'site_settings': site_settings,
        'stats': stats,
    }
    
    return render(request, 'dashboard/catalog/management.html', context)


# Ana sitede PDF görüntüleme view'ı
def catalog_view(request):
    """Katalog görüntüleme sayfası (PDF.js ile sayfa sayfa görüntüleme)"""
    from core.models import SiteSettings
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.http import Http404
    import os
    
    site_settings = SiteSettings.get_current()
    
    # Katalog aktif mi ve dosya var mı kontrol et
    if not site_settings.pdf_catalog_enabled:
        messages.error(request, 'Katalog şu anda aktif değil.')
        return redirect('home:home')
    
    if not site_settings.pdf_catalog_file:
        messages.error(request, 'Katalog dosyası bulunamadı.')
        return redirect('home:home')
    
    # PDF dosyasının fiziksel olarak var olup olmadığını kontrol et
    try:
        if not os.path.exists(site_settings.pdf_catalog_file.path):
            messages.error(request, 'PDF dosyası sunucuda bulunamadı.')
            return redirect('home:home')
    except (ValueError, AttributeError):
        messages.error(request, 'PDF dosyası erişilemez durumda.')
        return redirect('home:home')
    
    # PDF URL'ini tam olarak oluştur
    pdf_url = request.build_absolute_uri(site_settings.pdf_catalog_file.url)
    
    # Dosya boyutu ve diğer meta bilgileri
    file_stats = {}
    try:
        file_size = os.path.getsize(site_settings.pdf_catalog_file.path)
        if file_size < 1024:
            file_stats['size_display'] = f"{file_size} B"
        elif file_size < 1048576:  # 1MB
            file_stats['size_display'] = f"{round(file_size / 1024, 1)} KB"
        else:  # 1MB ve üzeri
            file_stats['size_display'] = f"{round(file_size / 1048576, 2)} MB"
        
        file_stats['size_bytes'] = file_size
    except Exception as e:
        print(f"Dosya boyutu hesaplama hatası: {e}")
        file_stats['size_display'] = "Bilinmiyor"
    
    # WhatsApp linki oluştur
    whatsapp_link = None
    if site_settings.whatsapp_number:
        clean_number = site_settings.whatsapp_number.replace('+', '').replace(' ', '').replace('-', '')
        catalog_message = f"Merhaba! {site_settings.pdf_catalog_title} hakkında bilgi almak istiyorum."
        whatsapp_link = f"https://wa.me/{clean_number}?text={catalog_message}"
    
    context = {
        'site_settings': site_settings,
        'pdf_url': pdf_url,
        'catalog_title': site_settings.pdf_catalog_title,
        'file_stats': file_stats,
        
        # Site bilgileri
        'site_name': site_settings.site_name,
        'primary_color': site_settings.primary_color,
        'secondary_color': site_settings.secondary_color,
        
        # İletişim bilgileri
        'contact_phone': site_settings.contact_phone,
        'whatsapp_link': whatsapp_link,
        
        # SEO ve Meta
        'meta_description': f"{site_settings.site_name} - {site_settings.pdf_catalog_title}. Tüm ürünlerimizi katalogumuzdan inceleyebilirsiniz.",
        'og_image': site_settings.site_logo.url if site_settings.site_logo else None,
        
        # PDF Viewer ayarları
        'pdf_viewer_settings': {
            'enable_thumbnails': True,
            'enable_fullscreen': True,
            'enable_download': True,
            'enable_print': True,
            'default_scale': 'page-width',
        },
        
        # Debug bilgileri (development için)
        'debug_info': {
            'pdf_exists': os.path.exists(site_settings.pdf_catalog_file.path),
            'pdf_path': site_settings.pdf_catalog_file.path,
            'pdf_url': pdf_url,
        } if request.user.is_staff else None,
    }
    
    return render(request, 'catalog/catalog_view.html', context)








#profil ayarları
@staff_member_required(login_url='dashboard:dashboard_login')
def profile_view(request):
    """Kullanıcı profil görüntüleme"""
    return render(request, 'dashboard/profile/profile.html', {
        'user': request.user
    })

@staff_member_required(login_url='dashboard:dashboard_login')
def profile_edit(request):
    """Kullanıcı profil düzenleme"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.')
            return redirect('dashboard:profile')
        else:
            messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'dashboard/profile/edit.html', {
        'form': form
    })

@staff_member_required(login_url='dashboard:dashboard_login')
def profile_password_change(request):
    """Kullanıcı şifre değiştirme"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Önemli!
            messages.success(request, 'Şifreniz başarıyla değiştirildi.')
            return redirect('dashboard:profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'dashboard/profile/password_change.html', {
        'form': form
    })

@staff_member_required(login_url='dashboard:dashboard_login')
def settings_view(request):
    """Genel ayarlar sayfası"""
    from core.models import SiteSettings
    
    site_settings = SiteSettings.get_current()
    
    context = {
        'site_settings': site_settings,
        'settings_tabs': [
            {'id': 'general', 'title': 'Genel Ayarlar', 'icon': 'fas fa-cog'},
            {'id': 'contact', 'title': 'İletişim Bilgileri', 'icon': 'fas fa-phone'},
            {'id': 'social', 'title': 'Sosyal Medya', 'icon': 'fas fa-share-alt'},
            {'id': 'seo', 'title': 'SEO Ayarları', 'icon': 'fas fa-search'},
            {'id': 'design', 'title': 'Tasarım', 'icon': 'fas fa-palette'},
        ]
    }
    
    return render(request, 'dashboard/settings/settings.html', context)

@staff_member_required(login_url='dashboard:dashboard_login')
def business_settings(request):
    """Site ayarları düzenleme - SiteSettings kullanarak"""
    from core.models import SiteSettings
    
    settings_obj = SiteSettings.get_current()
    
    if request.method == 'POST':
        form = BusinessSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            
            # Cache'i temizle
            from core.context_processors import clear_site_settings_cache
            clear_site_settings_cache()
            
            messages.success(request, 'Site ayarları başarıyla güncellendi.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Site ayarları başarıyla güncellendi.'
                })
            
            return redirect('dashboard:settings')
        else:
            messages.error(request, 'Form hatası! Lütfen alanları kontrol edin.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': dict(form.errors)
                })
    else:
        form = BusinessSettingsForm(instance=settings_obj)
    
    return render(request, 'dashboard/settings/business.html', {
        'form': form,
        'settings': settings_obj
    })
    
    
from core.utils import check_cloudinary_storage

def dashboard_index(request):
    # Mevcut kodlar...
    
    # Cloudinary alan kullanımı
    storage_info = check_cloudinary_storage()
    
    context = {
        # Mevcut context...
        'storage_info': storage_info,
    }
    return render(request, 'dashboard/index.html', context)



@staff_member_required
def storage_info_api(request):
    """Storage bilgilerini JSON olarak döner"""
    storage_info = check_cloudinary_storage()
    return JsonResponse(storage_info)