#core\reviews\apps.py
from django.apps import AppConfig

class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    verbose_name = 'Yorumlar'

    def ready(self):
        try:
            import reviews.translation  # Translation dosyasını import et
        except ImportError:
            pass