# dashboard/urls.py - Optimize edilmiş URL patterns
"""
Dashboard URL konfigürasyonu - Class-based view'lara güncellendi
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.DashboardLogoutView.as_view(), name='logout'),
    
    # Dashboard Home - Optimize edilmiş
    path('', views.dashboard_home, name='home'),
    path('home/', views.dashboard_home, name='dashboard_home'),
    path('api/charts/<str:chart_id>/', views.chart_data_api, name='chart_data_api'),

    # About - Optimize edilmiş
    path('about/', views.about_edit, name='dashboard_about_edit'),
    
    # Messages and Reviews - Optimize edilmiş  
    path('messages/', views.messages_list, name='dashboard_messages'),  
    path('message/delete/<int:pk>/', views.message_delete, name='message_delete'),
    path('review/toggle/<int:id>/', views.review_status_toggle, name='review_toggle'),
    path('review/delete/<int:id>/', views.review_delete, name='review_delete'),
    path('reviews/', views.review_list, name='reviews'),
    
    # Gallery - Optimize edilmiş (Class-based views)
    path('gallery/', views.gallery_list, name='dashboard_gallery'),
    path('gallery/add/', views.gallery_add, name='gallery_add'),
    path('gallery/edit/<int:pk>/', views.gallery_edit, name='gallery_edit'),
    path('gallery/delete/<int:pk>/', views.gallery_delete, name='gallery_delete'),  # ← MEVCUT, KONTROL ET
    
    # Media Mentions - Optimize edilmiş
    path('media-mentions/', views.media_mentions_list, name='dashboard_media_mentions'),
    path('media-mentions/add/', views.media_mention_add, name='media_mention_add'),
    path('media-mentions/edit/<int:pk>/', views.media_mention_edit, name='media_mention_edit'),
    path('media-mentions/delete/<int:pk>/', views.media_mention_delete, name='media_mention_delete'),
    
    # Categories - Optimize edilmiş
    path('categories/', views.categories_list, name='dashboard_categories'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('categories/<int:category_id>/products/', views.category_products, name='category_products'),
    
    # Products - Optimize edilmiş
    path('products/', views.products_list, name='dashboard_products'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),  # ← MEVCUT, KONTROL ET
    
    # Carousel - Optimize edilmiş
    path('carousel/', views.carousel_list, name='dashboard_carousel'),
    path('carousel/add/', views.carousel_add, name='carousel_add'),
    path('carousel/edit/<int:pk>/', views.carousel_edit, name='carousel_edit'),
    path('carousel/delete/<int:pk>/', views.carousel_delete, name='carousel_delete'),
    
    # Services - Optimize edilmiş
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/edit/<int:pk>/', views.service_edit, name='service_edit'),
    path('services/delete/<int:pk>/', views.service_delete, name='service_delete'),  # ← YENİ EKLENDİ
    path('services/footer-toggle/<int:pk>/', views.service_footer_toggle, name='service_footer_toggle'), #footer
    path('services/status-toggle/<int:pk>/', views.service_status_toggle, name='service_status_toggle'),

    
    
    # Team Members - Optimize edilmiş
    path('team/', views.team_member_list, name='team_member_list'),
    path('team/create/', views.team_member_create, name='team_member_create'),
    path('team/edit/<int:pk>/', views.team_member_edit, name='team_member_edit'),
    path('team/delete/<int:pk>/', views.team_member_delete, name='team_member_delete'),
    
    # User Management - Optimize edilmiş
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:user_id>/', views.user_delete, name='user_delete'),
    path('users/password-change/<int:user_id>/', views.user_password_change, name='user_password_change'),
    path('users/toggle-status/<int:user_id>/', views.user_toggle_status, name='user_toggle_status'),
    
    # Activities - Optimize edilmiş
    path('activities/', views.activities_list, name='activities_list'),
    
    # Notifications - Optimize edilmiş (AJAX endpoints)
    path('notifications/get/', views.get_notifications, name='get_notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/popup-content/', views.notification_popup_content, name='notification_popup_content'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    
    # Translation Settings - Optimize edilmiş
    path('translation-settings/', views.translation_settings, name='translation_settings'),
    
    #  PDF Katalog için eklenecek satır
    path('catalog/', views.pdf_catalog_management, name='pdf_catalog_management'),
    
    # API endpoint'i ekleyin
    path('api/storage-info/', views.storage_info_api, name='storage_info_api'),
    
    # Profil ve Ayarlar URL'leri
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password-change/', views.profile_password_change, name='profile_password_change'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/business/', views.business_settings, name='business_settings'),
    
    
    # PAROLA SIFIRLAMA URL'LERİ (Rate Limit Korumalı)
    path('password-reset/', views.DashboardPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.DashboardPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.DashboardPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.DashboardPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# AJAX ve API endpoint'leri için ek URL patterns
ajax_patterns = [
    # AJAX Gallery endpoints
    path('ajax/gallery/list/', views.gallery_list, name='ajax_gallery_list'),
    path('ajax/gallery/edit/<int:pk>/', views.gallery_edit, name='ajax_gallery_edit'),
    
    # AJAX Product endpoints  
    path('ajax/products/edit/<int:pk>/', views.product_edit, name='ajax_product_edit'),
    
    # AJAX Notification endpoints
    path('ajax/notifications/popup/', views.notification_popup_content, name='ajax_notification_popup'),
    path('ajax/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='ajax_mark_notification_read'),
]

# Ana URL patterns'a AJAX patterns'leri ekle
urlpatterns += ajax_patterns

# Backward compatibility için eski URL'leri redirect et
legacy_redirects = [
    # Eski dashboard URL'leri yeni optimize edilmiş URL'lere yönlendir
    path('dashboard/', views.dashboard_home, name='legacy_dashboard_home'),
    path('dashboard/messages/', views.messages_list, name='legacy_dashboard_messages'),
    path('dashboard/gallery/', views.gallery_list, name='legacy_dashboard_gallery'),
    path('dashboard/products/', views.products_list, name='legacy_dashboard_products'),
    

]

urlpatterns += legacy_redirects