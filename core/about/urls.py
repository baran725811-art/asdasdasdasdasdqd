# about/urls.py
from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    # Ana hakkımızda sayfası
    path('', views.about, name='about'),
    
    # Basın haberleri - YENİ EKLENEN
    path('basin-haberleri/', views.media_mentions_list, name='media_mentions'),
    
    # Hakkımızda detay (eğer birden fazla varsa)
    path('<slug:slug>/', views.about_detail, name='detail'),
    
    # Hizmetler
    path('hizmetler/', views.services, name='services'),
    path('hizmet/<slug:slug>/', views.service_detail, name='service_detail'),
    
    # Ekip
    path('ekip/', views.team, name='team'),
    path('ekip/<slug:slug>/', views.team_detail, name='team_detail'),
]