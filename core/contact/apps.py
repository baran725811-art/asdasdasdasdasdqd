# contact/apps.py
from django.apps import AppConfig

class ContactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contact'
    verbose_name = 'İletişim'

    def ready(self):
        try:
            import contact.translation
            import contact.signals  # Signal'leri yükle
        except ImportError:
            pass
