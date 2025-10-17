# reviews/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    name = models.CharField("Ad Soyad", max_length=100, default=" ")
    rating = models.IntegerField(
        verbose_name="Değerlendirme",
        validators=[
            MinValueValidator(1, "Değerlendirme 1'den küçük olamaz"),
            MaxValueValidator(5, "Değerlendirme 5'ten büyük olamaz")
        ]
    )
    comment = models.TextField(verbose_name="Yorum")
    image = models.ImageField(upload_to='reviews/%Y/%m/', verbose_name="Resim", blank=True, null=True)
    ip_address = models.GenericIPAddressField("IP Adresi", null=True, blank=True)  # Yeni eklendi
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    is_approved = models.BooleanField(default=False, verbose_name="Onaylı")

    class Meta:
        verbose_name = "Müşteri Yorumu"
        verbose_name_plural = "Müşteri Yorumları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} Yıldız"
    
ip_address = models.GenericIPAddressField(
    "IP Adresi",
    null=True,
    blank=True,
    help_text="Kullanıcının IP adresi otomatik olarak kaydedilir."
)