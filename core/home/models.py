#core\home\models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.urls import reverse
from core.cloudinary_fields import OptimizedImageField, SEOImageMixin

class CarouselSlide(SEOImageMixin, models.Model):
    title = models.CharField("Başlık", max_length=200)
    slug = models.SlugField("SEO URL", max_length=250, unique=True, blank=True,
                           help_text="Otomatik oluşturulur. Slide detay sayfası için kullanılır.")
    description = models.TextField("Açıklama")
    
    # Cloudinary ile değiştirildi - imagekit kaldırıldı
    image = OptimizedImageField("Orijinal Görsel", folder="carousel",
                               help_text="Tam boyut orijinal görsel (modal/detay için)")
    
    # Kırpılmış resim alanı
    cropped_image = OptimizedImageField("Kırpılmış Görsel", folder="carousel/cropped", blank=True,
                                       help_text="Carousel\'da gösterilecek kırpılmış görsel")
    
    # SEO için alt text alanı (güçlendirildi)
    alt_text = models.CharField(
        "Alt Metin (SEO)", 
        max_length=125,
        blank=True,
        help_text="Görsel için alternatif metin. SEO için önemli! (Max 125 karakter)"
    )
    
    
    
    # SEO Meta Fields
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    button_text = models.CharField("Buton Metni", max_length=50, blank=True)
    button_url = models.CharField("Buton URL", max_length=200, blank=True)
    order = models.PositiveIntegerField("Sıralama", default=0)
    is_active = models.BooleanField("Aktif", default=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)
    secondary_button_text = models.CharField(
        "İkinci Buton Metni", 
        max_length=50, 
        blank=True,
        default="Hakkımızda",
        help_text="Ana butonun yanındaki ikinci buton metni"
    )
    
    secondary_button_url = models.CharField(
        "İkinci Buton URL", 
        max_length=200, 
        blank=True,
        help_text="İkinci buton linki. Boş bırakılırsa hakkımızda sayfasına yönlendirir"
    )
    
    class Meta:
        ordering = ['order']
        verbose_name = "Carousel Slayt"
        verbose_name_plural = "Carousel Slaytlar"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Slug çakışması kontrolü
        original_slug = self.slug
        counter = 1
        while CarouselSlide.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('home:slide_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_active:
            active_slides = CarouselSlide.objects.filter(is_active=True)
            if self.pk:
                active_slides = active_slides.exclude(pk=self.pk)
            if active_slides.count() >= 5:
                raise ValidationError('En fazla 5 aktif slayt olabilir.')
        
        # SEOImageMixin'den clean çağır
        super().clean()
        
    def get_secondary_button_url(self):
        """İkinci buton URL'ini döndürür, yoksa hakkımızda sayfasını döndürür"""
        if self.secondary_button_url:
            return self.secondary_button_url
        else:
            try:
                from django.urls import reverse
                return reverse('about:about')
            except:
                return '/about/'