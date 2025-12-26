# about/management/commands/update_yearly_stats.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from about.models import About
from datetime import datetime


class Command(BaseCommand):
    help = 'Yıllık istatistikleri günceller (her yıl 1 Ocak\'ta çalıştırılmalı)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--increment-years',
            type=int,
            default=1,
            help='Tecrübe yılını kaç artıracağınızı belirtin (varsayılan: 1)'
        )

    def handle(self, *args, **options):
        try:
            # About model'i al (ilk kayıt)
            about = About.objects.first()
            if not about:
                self.stdout.write(
                    self.style.ERROR('About modeli bulunamadı!')
                )
                return

            # Mevcut değerleri al
            old_years_experience = about.years_experience

            # Tecrübe yılını artır
            increment = options['increment_years']
            about.years_experience += increment

            # Kaydet
            about.save()

            # Cache'i temizle
            cache.delete('about_info')
            cache.delete('site_settings')

            # Sonuç mesajı
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Yıllık istatistikler güncellendi!\n'
                    f'   Tecrübe: {old_years_experience} → {about.years_experience} yıl\n'
                    f'   Güncelleme tarihi: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
                )
            )

            # Özet bilgi
            self.stdout.write('\n📊 Güncel İstatistikler:')
            self.stdout.write(f'   • Tecrübe: {about.years_experience} yıl')
            self.stdout.write(f'   • Tamamlanan İş: {about.completed_jobs}')
            self.stdout.write(f'   • Mutlu Müşteri: {about.happy_customers}')
            self.stdout.write(f'   • Memnuniyet: %{about.customer_satisfaction}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Hata oluştu: {e}')
            )
