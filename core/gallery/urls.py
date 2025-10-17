# gallery/urls.py
from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    # Ana galeri sayfası
    path('', views.gallery_list, name='gallery_list'),
    
    # Medya tipi bazında filtreleme
    path('resimler/', views.gallery_images, name='gallery_images'),
    path('videolar/', views.gallery_videos, name='gallery_videos'),
    
    # Galeri detay sayfası
    path('<slug:slug>/', views.gallery_detail, name='detail'),
]