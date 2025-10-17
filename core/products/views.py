# products/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Product, Category

def product_list(request):
    """Ana ürün listesi sayfası"""
    products = Product.objects.filter(is_active=True).select_related('category')
    
    # Arama functionality
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Kategori filtresi
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=selected_category)
    
    # Sıralama
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(products, 12)  # Sayfa başına 12 ürün
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Kategoriler (sidebar için)
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('product', filter=Q(product__is_active=True))
    ).order_by('order', 'name')
    
    # Öne çıkan ürünler
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category')[:4]
    
    context = {
        'products': page_obj,
        'categories': categories,
        'featured_products': featured_products,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'page_obj': page_obj,
        
        # SEO Meta bilgileri
        'meta_title': 'Ürünlerimiz - Kaliteli Ürün Çeşitleri',
        'meta_description': 'Geniş ürün yelpazemizden ihtiyacınıza uygun kaliteli ürünleri keşfedin.',
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    """Ürün detay sayfası"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # İlgili ürünler (aynı kategoriden)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk).select_related('category')[:4]
    
    # Diğer önerilen ürünler (farklı kategorilerden)
    suggested_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).exclude(pk=product.pk).select_related('category')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'suggested_products': suggested_products,
        
        # SEO Meta bilgileri
        'meta_title': product.meta_title or f"{product.name} - {product.category.name}",
        'meta_description': product.meta_description or product.short_description or product.description[:160],
        
        # Structured Data için
        'breadcrumbs': [
            {'name': 'Ana Sayfa', 'url': '/'},
            {'name': 'Ürünler', 'url': '/urunler/'},
            {'name': product.category.name, 'url': product.category.get_absolute_url()},
            {'name': product.name, 'url': product.get_absolute_url()},
        ]
    }
    
    return render(request, 'products/product_detail.html', context)

def category_list(request):
    """Kategori listesi sayfası"""
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('product', filter=Q(product__is_active=True))
    ).order_by('order', 'name')
    
    context = {
        'categories': categories,
        'meta_title': 'Kategoriler - Ürün Kategorilerimiz',
        'meta_description': 'Tüm ürün kategorilerimizi görüntüleyin ve istediğiniz kategoriye kolayca ulaşın.',
    }
    
    return render(request, 'products/category_list.html', context)

def category_detail(request, slug):
    """Kategori detay sayfası"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')
    
    # Sıralama
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Diğer kategoriler
    other_categories = Category.objects.filter(
        is_active=True
    ).exclude(pk=category.pk).annotate(
        product_count=Count('product', filter=Q(product__is_active=True))
    ).order_by('order', 'name')[:6]
    
    context = {
        'category': category,
        'products': page_obj,
        'other_categories': other_categories,
        'sort_by': sort_by,
        'page_obj': page_obj,
        
        # SEO Meta bilgileri
        'meta_title': category.meta_title or f"{category.name} - Ürün Kategorisi",
        'meta_description': category.meta_description or category.description[:160],
        
        # Structured Data için
        'breadcrumbs': [
            {'name': 'Ana Sayfa', 'url': '/'},
            {'name': 'Ürünler', 'url': '/urunler/'},
            {'name': category.name, 'url': category.get_absolute_url()},
        ]
    }
    
    return render(request, 'products/category_detail.html', context)

def featured_products(request):
    """Öne çıkan ürünler sayfası"""
    products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category').order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_title': 'Öne Çıkan Ürünler',
        'page_obj': page_obj,
        
        # SEO Meta bilgileri
        'meta_title': 'Öne Çıkan Ürünler - En Popüler Ürünlerimiz',
        'meta_description': 'En çok tercih edilen ve öne çıkan ürünlerimizi keşfedin.',
    }
    
    return render(request, 'products/featured_products.html', context)

def discounted_products(request):
    """İndirimli ürünler sayfası"""
    products = Product.objects.filter(
        is_active=True,
        discount_price__isnull=False
    ).select_related('category').order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_title': 'İndirimli Ürünler',
        'page_obj': page_obj,
        
        # SEO Meta bilgileri
        'meta_title': 'İndirimli Ürünler - Fırsat Ürünleri',
        'meta_description': 'İndirimli ürünlerimizi kaçırmayın! Özel fiyatlarla kaliteli ürünler.',
    }
    
    return render(request, 'products/discounted_products.html', context)