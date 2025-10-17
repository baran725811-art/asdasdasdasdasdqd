# dashboard/signals.py - yeni dosya oluşturun
from django.db.models.signals import post_save
from django.dispatch import receiver
from contact.models import Contact
from reviews.models import Review
from products.models import Product
from .models import MediaMention
from .utils import create_message_notification, create_review_notification, create_product_notification

@receiver(post_save, sender=Contact)
def create_message_notification_signal(sender, instance, created, **kwargs):
    """Yeni mesaj geldiğinde bildirim oluştur"""
    if created:
        create_message_notification(instance)

@receiver(post_save, sender=Review)
def create_review_notification_signal(sender, instance, created, **kwargs):
    """Yeni yorum geldiğinde bildirim oluştur"""
    if created:
        create_review_notification(instance)

@receiver(post_save, sender=Product)
def create_product_notification_signal(sender, instance, created, **kwargs):
    """Yeni ürün eklendiğinde bildirim oluştur"""
    if created:
        create_product_notification(instance)