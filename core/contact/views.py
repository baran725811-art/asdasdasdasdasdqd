from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from .forms import ContactForm
from reviews.forms import ReviewForm
from reviews.models import Review
from django.utils.translation import gettext as _

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def contact(request):
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        if 'form_type' in request.POST:
            if request.POST['form_type'] == 'contact':
                contact_form = ContactForm(request.POST)
                review_form = ReviewForm()
                if contact_form.is_valid():
                    contact_form.save()
                    messages.success(request, _('Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.'))
                    return redirect('contact:contact')
                else:
                    messages.error(request, _('Form gönderilirken hata oluştu. Lütfen bilgileri kontrol edin.'))
            
            elif request.POST['form_type'] == 'review':
                review_form = ReviewForm(request.POST, request.FILES)
                contact_form = ContactForm()
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.ip_address = get_client_ip(request)
                    review.save()
                    messages.success(request, _('Değerlendirmeniz başarıyla kaydedildi. Onaylandıktan sonra yayınlanacaktır.'))
                    return redirect('contact:contact')
                else:
                    messages.error(request, _('Değerlendirme gönderilirken hata oluştu.'))


    else:
        contact_form = ContactForm()
        review_form = ReviewForm()

    context = {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': reviews,
    }
    return render(request, 'contact/contact.html', context)