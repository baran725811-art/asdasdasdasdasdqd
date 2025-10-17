#core\products\apps.py
from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = 'Ürünler'

    def ready(self):
        try:
            import products.translation  # Translation dosyasını import et
        except ImportError:
            pass