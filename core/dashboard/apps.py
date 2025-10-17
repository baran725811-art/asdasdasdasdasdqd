# dashboard/apps.py - değiştirilecek kısım
from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    verbose_name = 'Dashboard'
    
    def ready(self):
        import dashboard.signals  # Signals'ları import et