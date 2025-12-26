# reviews/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Review
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Review)
def update_statistics_on_review(sender, instance, created, **kwargs):
    """
    Yorum onaylandığında veya güncellendiğinde istatistikleri güncelle

    Kurallar:
    - Her onaylı yorum → tamamlanan iş +1
    - 2+ puanlı yorumlar → mutlu müşteri +1
    - Ortalama puan → memnuniyet % hesapla
    """
    try:
        from about.models import About

        # About model'i al (ilk kayıt)
        about = About.objects.first()
        if not about:
            logger.warning("About modeli bulunamadı, istatistik güncellenemedi")
            return

        # Sadece onaylı yorumlar için istatistik güncelle
        if instance.is_approved:
            # Tamamlanan işi arttır (her onaylı yorum için +1)
            # NOT: Sadece yeni oluşturulduğunda veya onay durumu değiştiğinde arttır
            if created or (hasattr(instance, '_state') and instance._state.fields_cache.get('is_approved') != instance.is_approved):
                from django.db.models import F
                About.objects.filter(pk=about.pk).update(
                    completed_jobs=F('completed_jobs') + 1
                )

            # Mutlu müşteriler = 2+ puan veren yorumlar
            happy_customers_count = Review.objects.filter(
                is_approved=True,
                rating__gte=2
            ).count()
            about.happy_customers = happy_customers_count

            # Müşteri memnuniyeti = ortalama puan (yüzde olarak)
            # 5 üzerinden ortalama alıp 100'e çeviriyoruz
            from django.db.models import Avg
            avg_rating = Review.objects.filter(is_approved=True).aggregate(
                Avg('rating')
            )['rating__avg'] or 0

            # 5 üzerinden ortalamayı 100 üzerinden puana çeviriyoruz
            about.customer_satisfaction = int((avg_rating / 5) * 100)

            about.save()

            # Cache'i temizle
            cache.delete('about_info')
            cache.delete('site_settings')

            logger.info(
                f"İstatistikler güncellendi: "
                f"Tamamlanan İş={about.completed_jobs}, "
                f"Mutlu Müşteri={about.happy_customers}, "
                f"Memnuniyet=%{about.customer_satisfaction}"
            )

    except Exception as e:
        logger.error(f"İstatistik güncelleme hatası: {e}")


@receiver(post_delete, sender=Review)
def update_statistics_on_review_delete(sender, instance, **kwargs):
    """
    Yorum silindiğinde istatistikleri güncelle
    """
    try:
        from about.models import About

        about = About.objects.first()
        if not about:
            return

        # Tamamlanan işi azalt (yorum silindi)
        if instance.is_approved:
            from django.db.models import F
            About.objects.filter(pk=about.pk).update(
                completed_jobs=F('completed_jobs') - 1
            )

        # Mutlu müşteriler
        happy_customers_count = Review.objects.filter(
            is_approved=True,
            rating__gte=2
        ).count()
        about.happy_customers = happy_customers_count

        # Müşteri memnuniyeti
        from django.db.models import Avg
        avg_rating = Review.objects.filter(is_approved=True).aggregate(
            Avg('rating')
        )['rating__avg'] or 0
        about.customer_satisfaction = int((avg_rating / 5) * 100)

        about.save()

        # Cache'i temizle
        cache.delete('about_info')
        cache.delete('site_settings')

        logger.info("Yorum silindi, istatistikler güncellendi")

    except Exception as e:
        logger.error(f"İstatistik güncelleme hatası (silme): {e}")
