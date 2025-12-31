# about/signals.py - YENİ DOSYA OLUŞTUR
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import About

@receiver(post_save, sender=About)
def clear_about_cache_on_save(sender, instance, **kwargs):
    """About modeli kaydedildiğinde cache'i temizle"""
    cache.delete('about_info')
    cache.delete('site_settings')  # Context processor cache'ini de temizle

@receiver(post_delete, sender=About)
def clear_about_cache_on_delete(sender, instance, **kwargs):
    """About modeli silindiğinde cache'i temizle"""
    cache.delete('about_info')
    cache.delete('site_settings')