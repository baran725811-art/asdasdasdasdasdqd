from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Mevcut ürünler için SKU oluştur'
    
    def handle(self, *args, **options):
        products = Product.objects.filter(sku__isnull=True) | Product.objects.filter(sku='')
        count = 0
        
        for product in products:
            old_sku = product.sku
            product.sku = product.generate_sku()
            product.save()
            
            self.stdout.write(f"✓ {product.name}: {old_sku or 'Boş'} → {product.sku}")
            count += 1
        
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'\n{count} ürün için SKU oluşturuldu'))
        else:
            self.stdout.write(self.style.WARNING('Tüm ürünlerde SKU mevcut'))