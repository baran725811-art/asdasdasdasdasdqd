from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from django_ratelimit.decorators import ratelimit
from django.utils.translation import gettext as _
from .models import Review
from .forms import ReviewForm

@login_required
@ratelimit(key='user', rate='3/h', method='POST', block=True)
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, _('Yorumunuz başarıyla alındı. İncelendikten sonra yayınlanacaktır.'))
            return redirect('home:index')
        else:
            messages.error(request, _('Form gönderilirken hata oluştu. Lütfen bilgileri kontrol edin.'))
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'title': _('Yorum Ekle')
    }
    return render(request, 'reviews/review_form.html', context)

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