from django.core.management.base import BaseCommand
from core.utils import check_cloudinary_storage

class Command(BaseCommand):
    help = 'Cloudinary storage kullanımını kontrol eder'

    def handle(self, *args, **options):
        storage_info = check_cloudinary_storage()
        
        self.stdout.write(f"Paket: {storage_info['limit_gb']}GB")
        self.stdout.write(f"Kullanım: {storage_info['used_gb']}GB (%{storage_info['usage_percentage']})")
        self.stdout.write(f"Kalan: {storage_info['remaining_gb']}GB")
        
        if storage_info['is_critical']:
            self.stdout.write(self.style.ERROR('UYARI: Depolama alanı kritik seviyede!'))
        elif storage_info['is_warning']:
            self.stdout.write(self.style.WARNING('Depolama alanı %80 dolu.'))