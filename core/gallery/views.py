# gallery/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Gallery

def gallery_list(request):
    """Tüm galeri öğeleri listesi"""
    gallery_items = Gallery.objects.filter(is_active=True).order_by('order', '-created_at')
    
    # Pagination
    paginator = Paginator(gallery_items, 12)  # Sayfa başına 12 öğe
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Öne çıkan öğeler
    featured_items = Gallery.objects.filter(
        is_active=True, 
        is_featured=True
    ).order_by('order')[:6]
    
    # Medya tipleri istatistikleri
    total_images = Gallery.objects.filter(is_active=True, media_type='image').count()
    total_videos = Gallery.objects.filter(is_active=True, media_type='video').count()
    
    context = {
        'gallery_items': page_obj,
        'featured_items': featured_items,
        'total_images': total_images,
        'total_videos': total_videos,
        'page_obj': page_obj,
        
        # SEO Meta bilgileri
        'meta_title': 'Galeri - Projelerimiz ve Çalışmalarımız',
        'meta_description': 'Gerçekleştirdiğimiz projelerin fotoğraf ve videolarını galeri sayfamızda inceleyebilirsiniz.',
    }
    
    return render(request, 'gallery/gallery_list.html', context)

def gallery_images(request):
    """Sadece resim galerisi"""
    gallery_items = Gallery.objects.filter(
        is_active=True, 
        media_type='image'
    ).order_by('order', '-created_at')
    
    # Pagination
    paginator = Paginator(gallery_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'gallery_items': page_obj,
        'media_type': 'image',
        'page_obj': page_obj,
        
        # SEO Meta bilgileri
        'meta_title': 'Resim Galerisi - Projelerimizin Fotoğrafları',
        'meta_description': 'Tamamladığımız projelerin detaylı fotoğraflarını resim galerimizdeki inceleyin.',
    }
    
    return render(request, 'gallery/gallery_images.html', context)

def gallery_videos(request):
    """Sadece video galerisi"""
    gallery_items = Gallery.objects.filter(
        is_active=True, 
        media_type='video'
    ).order_by('order', '-created_at')
    
    # Pagination
    paginator = Paginator(gallery_items, 9)  # Video için sayfa başına 9 öğe
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'gallery_items': page_obj,
        'media_type': 'video',
        'page_obj': page_obj,
        
        # SEO Meta bilgileri
        'meta_title': 'Video Galerisi - Projelerimizin Videoları',
        'meta_description': 'Projelerimizin detaylı videolarını video galerimizdeki izleyebilirsiniz.',
    }
    
    return render(request, 'gallery/gallery_videos.html', context)

def gallery_detail(request, slug):
    """Galeri öğesi detay sayfası"""
    gallery_item = get_object_or_404(Gallery, slug=slug, is_active=True)
    
    # İlgili diğer öğeler (aynı medya tipinden)
    related_items = Gallery.objects.filter(
        is_active=True,
        media_type=gallery_item.media_type
    ).exclude(pk=gallery_item.pk).order_by('order', '-created_at')[:6]
    
    # Önceki ve sonraki öğeler
    all_items = Gallery.objects.filter(is_active=True).order_by('order', '-created_at')
    current_index = None
    
    for i, item in enumerate(all_items):
        if item.pk == gallery_item.pk:
            current_index = i
            break
    
    previous_item = None
    next_item = None
    
    if current_index is not None:
        if current_index > 0:
            previous_item = all_items[current_index - 1]
        if current_index < len(all_items) - 1:
            next_item = all_items[current_index + 1]
    
    context = {
        'gallery_item': gallery_item,
        'related_items': related_items,
        'previous_item': previous_item,
        'next_item': next_item,
        
        # SEO Meta bilgileri
        'meta_title': gallery_item.meta_title or f"{gallery_item.title} - Galeri",
        'meta_description': gallery_item.meta_description or gallery_item.description[:160],
        
        # Structured Data için
        'breadcrumbs': [
            {'name': 'Ana Sayfa', 'url': '/'},
            {'name': 'Galeri', 'url': '/galeri/'},
            {'name': gallery_item.title, 'url': gallery_item.get_absolute_url()},
        ]
    }
    
    return render(request, 'gallery/gallery_detail.html', context)