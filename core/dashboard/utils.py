# dashboard/utils.py 
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Notification
from .translation_utils import TranslationManager


class NotificationManager:
    """Bildirim yönetimi için merkezi sınıf"""
    
    @staticmethod
    def create_notification(title, message, notification_type, content_object=None, redirect_url=''):
        """
        Bildirim oluşturma fonksiyonu
        """
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            redirect_url=redirect_url
        )
        
        if content_object:
            notification.content_type = ContentType.objects.get_for_model(content_object)
            notification.object_id = content_object.pk
        
        notification.save()
        return notification

    @staticmethod
    def create_message_notification(message_obj):
        """Mesaj bildirimi oluştur"""
        return NotificationManager.create_notification(
            title=f"Yeni mesaj: {message_obj.subject}",
            message=f"{message_obj.name} tarafından gönderildi",
            notification_type='message',
            content_object=message_obj,
            redirect_url='/dashboard/messages/'
        )

    @staticmethod
    def create_review_notification(review_obj):
        """Yorum bildirimi oluştur"""
        return NotificationManager.create_notification(
            title=f"Yeni yorum ({review_obj.rating} yıldız)",
            message=f"{review_obj.name} tarafından yapıldı",
            notification_type='review',
            content_object=review_obj,
            redirect_url='/dashboard/reviews/'
        )

    @staticmethod
    def create_product_notification(product_obj):
        """Ürün bildirimi oluştur"""
        return NotificationManager.create_notification(
            title=f"Yeni ürün eklendi: {product_obj.name}",
            message=f"{product_obj.category.name} kategorisinde",
            notification_type='product',
            content_object=product_obj,
            redirect_url='/dashboard/products/'
        )


class DashboardResponseHelper:
    """Dashboard response'larını yöneten yardımcı sınıf"""
    
    @staticmethod
    def handle_form_success(request, message, redirect_url, ajax_response_data=None):
        """Form başarı durumunu işle"""
        messages.success(request, message)
        
        # AJAX isteği ise JSON response döndür
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response_data = {'success': True, 'message': message}
            if ajax_response_data:
                response_data.update(ajax_response_data)
            return JsonResponse(response_data)
        
        return redirect(redirect_url)
    
    @staticmethod
    def handle_form_error(request, form, error_message, ajax_template=None, ajax_context=None):
        """Form hata durumunu işle"""
        messages.error(request, error_message)
        
        # AJAX isteği ise hata mesajı döndür
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response_data = {'success': False, 'errors': form.errors}
            
            # Template varsa modal içeriği de döndür
            if ajax_template and ajax_context:
                modal_content = render_to_string(ajax_template, ajax_context)
                response_data['modal_content'] = modal_content
                
            return JsonResponse(response_data)
        
        return None  # Normal form handling devam etsin
    
    @staticmethod
    def render_ajax_modal(template_path, context):
        """AJAX modal içeriği döndür"""
        modal_content = render_to_string(template_path, context)
        return JsonResponse({'modal_content': modal_content})


class FormHelper:
    """Form işlemleri için yardımcı fonksiyonlar"""
    
    @staticmethod
    def setup_translation_form(form_class, request, instance=None):
        """Çeviri destekli form hazırla"""
        translation_data = TranslationManager.get_user_translation_settings(request.user)
        
        form_kwargs = {
            'instance': instance,
            'user': request.user,
            **translation_data
        }
        
        if request.method == 'POST':
            form_kwargs.update({
                'data': request.POST,
                'files': request.FILES
            })
        
        return form_class(**form_kwargs)
    
    @staticmethod
    def handle_translation_form_submission(form, request, success_message, redirect_url):
        """Çeviri form gönderimini işle"""
        if form.is_valid():
            try:
                saved_object = form.save()
                return DashboardResponseHelper.handle_form_success(
                    request, success_message, redirect_url
                )
            except Exception as e:
                messages.error(request, f'Kaydetme hatası: {str(e)}')
        else:
            # Çeviri hatalarını işle
            translation_data = TranslationManager.get_user_translation_settings(request.user)
            TranslationManager.handle_translation_form_errors(
                form, translation_data['enabled_languages'], request
            )
        
        return None  # Form handling devam etsin


# Backward compatibility için eski fonksiyonları koru
def create_notification(title, message, notification_type, content_object=None, redirect_url=''):
    return NotificationManager.create_notification(title, message, notification_type, content_object, redirect_url)

def create_message_notification(message_obj):
    return NotificationManager.create_message_notification(message_obj)

def create_review_notification(review_obj):
    return NotificationManager.create_review_notification(review_obj)

def create_product_notification(product_obj):
    return NotificationManager.create_product_notification(product_obj)