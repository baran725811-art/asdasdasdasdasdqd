from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from django_ratelimit.decorators import ratelimit
from django.utils.translation import gettext as _
from .models import Review
from .forms import ReviewForm

def get_client_ip(request):
    """Kullanıcının IP adresini al"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@ratelimit(key='ip', rate='5/h', method='POST', block=True)  # ← IP bazlı limit
def add_review(request):
    if request.method == 'POST':
        # Giriş kontrolü YOK - herkes gönderebilir
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            # IP adresini kaydet (spam önleme için)
            review.ip_address = get_client_ip(request)  # ← Spam koruması
            review.save()



def review_list(request):
    # select_related('user') kısmını kaldırın çünkü user field'ı yok
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Sayfalama
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    
    context = {
        'reviews': reviews,
        'average_rating': round(average_rating, 1) if average_rating else 0,
        'total_reviews': Review.objects.filter(is_approved=True).count(),
        'title': _('Müşteri Yorumları')
    }
    return render(request, 'contact/sections/review_list.html', context)