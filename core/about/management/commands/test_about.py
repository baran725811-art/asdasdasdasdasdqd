# about/management/__init__.py - BOŞ DOSYA OLUŞTUR

# about/management/commands/__init__.py - BOŞ DOSYA OLUŞTUR  

# about/management/commands/test_about.py - TEST KOMUTU
from django.core.management.base import BaseCommand
from django.core.cache import cache
from about.models import About

class Command(BaseCommand):
    help = 'About model test ve cache durumu kontrol et'

    def handle(self, *args, **options):
        self.stdout.write('=== ABOUT MODEL TEST ===')
        
        # About objesi kontrol et
        try:
            about = About.objects.get(pk=1)
            self.stdout.write(f'✅ About bulundu - ID: {about.id}')
            self.stdout.write(f'   Title: {about.title}')
            self.stdout.write(f'   Years Experience: {about.years_experience}')
            self.stdout.write(f'   Updated: {about.updated_at}')
        except About.DoesNotExist:
            self.stdout.write('❌ About objesi bulunamadı!')
            
            # Varsayılan oluştur
            about = About.objects.create(
                title='Test Hakkımızda',
                short_description='Test açıklama',
                mission='Test misyon',
                vision='Test vizyon',
                story='Test hikaye',
                years_experience=25,
                completed_jobs=6000,
                happy_customers=1200,
                total_services=15,
                customer_satisfaction=95,
            )
            self.stdout.write(f'✅ Test About oluşturuldu - ID: {about.id}')
        
        # Cache kontrol et
        self.stdout.write('\n=== CACHE DURUMU ===')
        about_cache = cache.get('about_info')
        if about_cache:
            self.stdout.write('✅ About cache var')
            self.stdout.write(f'   Cached title: {about_cache.get("title")}')
        else:
            self.stdout.write('❌ About cache yok')
        
        # Cache'i temizle ve tekrar test et
        self.stdout.write('\n=== CACHE TEMİZLEME TEST ===')
        cache.delete('about_info')
        cache.delete('site_settings')
        self.stdout.write('✅ Cache temizlendi')
        
        # Context processor test et
        from core.context_processors import seo_context
        from django.http import HttpRequest
        
        request = HttpRequest()
        request.method = 'GET'
        request.META = {'HTTP_HOST': 'testserver'}
        
        try:
            context = seo_context(request)
            self.stdout.write('\n=== CONTEXT PROCESSOR TEST ===')
            self.stdout.write(f'✅ Global about title: {context.get("global_about", {}).get("title")}')
            self.stdout.write(f'✅ Company years: {context.get("company_years_experience")}')
            self.stdout.write(f'✅ Company jobs: {context.get("company_completed_jobs")}')
        except Exception as e:
            self.stdout.write(f'❌ Context processor hatası: {e}')
        
        self.stdout.write('\n=== TEST TAMAMLANDI ===')
        self.stdout.write('Şimdi dashboard\'da değişiklik yapıp ana sayfayı kontrol edin!')