from django import template
from django.conf import settings
from core.models import SiteSettings

register = template.Library()

@register.simple_tag(takes_context=True)
def get_available_site_languages(context):
    """Dashboard'da seçilen aktif dilleri getir"""
    request = context['request']
    
    # Çeviri sistemi aktif mi?
    try:
        site_settings = SiteSettings.objects.get()
        if not site_settings.translation_enabled:
            return []
    except SiteSettings.DoesNotExist:
        return []
    
    # Admin ayarlarından dilleri al
    try:
        from dashboard.models import DashboardTranslationSettings
        
        admin_settings = DashboardTranslationSettings.objects.filter(
            user__is_staff=True
        ).order_by('-updated_at').first()
        
        if admin_settings:
            # Ana dil + ek diller
            all_languages = admin_settings.get_all_languages()
        else:
            all_languages = ['tr']
            
    except Exception as e:
        all_languages = ['tr']
    
    # Dil adlarıyla birlikte döndür
    language_dict = dict(settings.LANGUAGES)
    available_languages = []
    
    for lang_code in all_languages:
        if lang_code in language_dict:
            available_languages.append((lang_code, language_dict[lang_code]))
    
    return available_languages


@register.simple_tag
def get_current_language():
    """Mevcut aktif dil kodunu döndür"""
    from django.utils import translation
    return translation.get_language()



