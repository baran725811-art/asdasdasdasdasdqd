# about/apps.py - SİGNALLERİ BAĞLA
from django.apps import AppConfig

class AboutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'about'
    verbose_name = 'Hakkımızda'

    def ready(self):
        """Uygulama hazır olduğunda sinyalleri import et"""
        try:
            import about.signals  # signals.py dosyasını import et
            print("✅ About signals loaded successfully")
        except ImportError:
            print("❌ About signals import failed")