# about/urls.py
from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    # Önce SPESİFİK yollar (önemli!)
    path('hizmetler/', views.services, name='services'),
    path('ekip/', views.team, name='team'),
    path('basin-haberleri/', views.media_mentions_list, name='media_mentions'),
    
    # Sonra hizmet ve ekip detayları
    path('hizmet/<slug:slug>/', views.service_detail, name='service_detail'),
    path('ekip/<slug:slug>/', views.team_detail, name='team_detail'),
    
    # Ana hakkımızda sayfası
    path('', views.about, name='about'),
    
    # EN SONDA genel slug pattern
    path('<slug:slug>/', views.about_detail, name='detail'),
]