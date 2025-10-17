#core\products\urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Ana ürünler sayfası
    path('', views.product_list, name='product_list'),
    
    # Kategoriler
    path('kategoriler/', views.category_list, name='category_list'),
    path('kategori/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Özel sayfalar
    path('one-cikan/', views.featured_products, name='featured_products'),
    path('indirimli/', views.discounted_products, name='discounted_products'),
    
    # Ürün detayı (en sona koyuyoruz çakışma olmasın diye)
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]