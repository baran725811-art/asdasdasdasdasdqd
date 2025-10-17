# core/translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import SiteSettings

class SiteSettingsTranslationOptions(TranslationOptions):
    fields = (
        'site_name', 
        'site_tagline', 
        'seo_title', 
        'seo_description', 
        'seo_keywords',
        'pdf_catalog_title',
        'contact_address'
    )

translator.register(SiteSettings, SiteSettingsTranslationOptions)