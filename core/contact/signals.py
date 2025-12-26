# contact/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Contact
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Contact)
def update_statistics_on_contact(sender, instance, created, **kwargs):
    """
    İletişim mesajı geldiğinde istatistikleri güncelle

    Kural:
    - Her iletişim mesajı → tamamlanan iş sayısını arttır
    """
    if not created:
        # Sadece yeni mesajlarda istatistik güncelle
        return

    try:
        from about.models import About

        # About model'i al (ilk kayıt)
        about = About.objects.first()
        if not about:
            logger.warning("About modeli bulunamadı, istatistik güncellenemedi")
            return

        # Tamamlanan işi arttır (her yeni iletişim mesajı için +1)
        from django.db.models import F
        About.objects.filter(pk=about.pk).update(
            completed_jobs=F('completed_jobs') + 1
        )

        # Cache'i temizle
        cache.delete('about_info')
        cache.delete('site_settings')

        logger.info(
            f"İstatistikler güncellendi (iletişim): "
            f"Tamamlanan İş={about.completed_jobs}"
        )

    except Exception as e:
        logger.error(f"İletişim istatistik güncelleme hatası: {e}")


@receiver(post_delete, sender=Contact)
def update_statistics_on_contact_delete(sender, instance, **kwargs):
    """
    İletişim mesajı silindiğinde istatistikleri güncelle
    """
    try:
        from about.models import About
        from reviews.models import Review

        about = About.objects.first()
        if not about:
            return

        # Tamamlanan işi azalt (iletişim mesajı silindi)
        from django.db.models import F
        About.objects.filter(pk=about.pk).update(
            completed_jobs=F('completed_jobs') - 1
        )

        # Cache'i temizle
        cache.delete('about_info')
        cache.delete('site_settings')

        logger.info("İletişim mesajı silindi, istatistikler güncellendi")

    except Exception as e:
        logger.error(f"İletişim istatistik güncelleme hatası (silme): {e}")
