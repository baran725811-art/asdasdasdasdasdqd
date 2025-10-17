# dashboard/constants.py
"""
Dashboard için ortak sabitler ve konfigürasyonlar
"""

# Dil sabitleri - tek yerden yönetim
LANGUAGE_CHOICES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('es', 'Español'),
    ('ru', 'Русский'),
    ('ar', 'العربية'),
]

# Dil kodları ve isimleri mapping
LANGUAGE_NAMES = {
    'tr': 'Türkçe',
    'en': 'İngilizce',
    'de': 'Almanca',
    'fr': 'Fransızca',
    'es': 'İspanyolca',
    'ru': 'Rusça',
    'ar': 'Arapça'
}

# Desteklenen diller (Türkçe hariç)
SUPPORTED_LANGUAGES = ['en', 'de', 'fr', 'es', 'ru', 'ar']

# Form widget ortak CSS class'ları
FORM_WIDGET_CLASSES = {
    'text': 'form-control form-control-modern',
    'textarea': 'form-control form-control-modern',
    'select': 'form-control form-control-modern',
    'checkbox': 'form-check-input',
    'file': 'form-control form-control-modern',
    'date': 'form-control form-control-modern',
    'number': 'form-control form-control-modern',
    'url': 'form-control form-control-modern',
    'email': 'form-control form-control-modern',
}

# Model'lerde çeviri gerekli olan alanlar
TRANSLATION_REQUIRED_FIELDS = {
    'About': ['title', 'short_description', 'mission', 'vision', 'story'],
    'Service': ['title', 'description'],
    'TeamMember': ['name', 'position', 'bio'],
    'Product': ['name', 'description'],
    'Category': ['name', 'description'],
    'Gallery': ['title', 'description', 'alt_text'], 
    'CarouselSlide': ['title', 'description', 'alt_text', 'button_text'],
    'MediaMention': ['title', 'source', 'description'],
}

# Bildirim türleri
NOTIFICATION_TYPES = [
    ('message', 'Yeni Mesaj'),
    ('review', 'Yeni Yorum'),
    ('product', 'Yeni Ürün'),
    ('media_mention', 'Yeni Basın Haberi'),
    ('system', 'Sistem Bildirimi'),
]