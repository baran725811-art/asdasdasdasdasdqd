from django.apps import AppConfig

class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'
    verbose_name = 'Galeri'

    def ready(self):
        try:
            import gallery.translation  # Tam path ile import
        except ImportError:
            pass