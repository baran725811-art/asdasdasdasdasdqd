#core\contact\models.py
from django.db import models
from django.core.validators import MinValueValidator

class Contact(models.Model):
    name = models.CharField("Ad Soyad", max_length=100)
    email = models.EmailField("E-posta")
    phone = models.CharField("Telefon", max_length=20)
    subject = models.CharField("Konu", max_length=200)
    message = models.TextField("Mesaj")
    ip_address = models.GenericIPAddressField("IP Adresi", null=True, blank=True)  # Yeni eklendi
    created_at = models.DateTimeField("Gönderim Tarihi", auto_now_add=True)
    is_read = models.BooleanField("Okundu", default=False)

    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
ip_address = models.GenericIPAddressField(
    "IP Adresi",
    null=True,
    blank=True,
    help_text="Kullanıcının IP adresi otomatik olarak kaydedilir."
)   