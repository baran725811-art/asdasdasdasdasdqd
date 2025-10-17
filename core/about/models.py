#core\about\models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from core.cloudinary_fields import OptimizedImageField, SEOImageMixin

class About(SEOImageMixin, models.Model):
    title = models.CharField("Başlık", max_length=200)
    slug = models.SlugField("SEO URL", max_length=250, unique=True, blank=True,
                           help_text="Otomatik oluşturulur. SEO dostu URL için kullanılır.")
    short_description = models.TextField("Kısa Açıklama", null=True, blank=True)
    
    mission = models.TextField("Misyonumuz", null=True, blank=True)
    vision = models.TextField("Vizyonumuz", null=True, blank=True)
    story = models.TextField("Hikayemiz", null=True, blank=True)
    
    # Cloudinary ile değiştirildi
    image = OptimizedImageField("Orijinal Resim", folder="about", null=True, blank=True,
                               help_text="Tam boyut orijinal resim (modal/detay için)")
    
    # Kırpılmış resim alanı
    cropped_image = OptimizedImageField("Kırpılmış Resim", folder="about/cropped", blank=True,
                                       help_text="Kartlarda gösterilecek kırpılmış resim")
    
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True, 
                               help_text="Görsel için SEO alt metni (max 125 karakter)")
    
    years_experience = models.PositiveIntegerField("Tecrübe (Yıl)", default=20)
    completed_jobs = models.PositiveIntegerField("Tamamlanan İşler", default=5000)
    happy_customers = models.PositiveIntegerField("Mutlu Müşteriler", default=1000)
    total_services = models.PositiveIntegerField("Toplam Hizmet", default=10)
    customer_satisfaction = models.PositiveIntegerField("Müşteri Memnuniyeti (%)", default=100)
    
    # SEO Meta Fields
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hakkımızda"
        verbose_name_plural = "Hakkımızda"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Slug çakışması kontrolü
        original_slug = self.slug
        counter = 1
        while About.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('about:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title



class Service(SEOImageMixin, models.Model):
    title = models.CharField("Başlık", max_length=200)
    slug = models.SlugField("SEO URL", max_length=250, unique=True, blank=True,
                           help_text="Otomatik oluşturulur. SEO dostu URL için kullanılır.")
    description = models.TextField("Açıklama")
    
    # Cloudinary ile değiştirildi
    image = OptimizedImageField("Orijinal Resim", folder="services",
                               help_text="Hizmet için tam boyut orijinal resim")
    
    # Kırpılmış resim alanı  
    cropped_image = OptimizedImageField("Kırpılmış Resim", folder="services/cropped", blank=True,
                                       help_text="Hizmet kartlarında gösterilecek kırpılmış resim")
    
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True,
                               help_text="Hizmet görseli için SEO alt metni")
    
    # *** YENİ ALAN - FOOTER İÇİN ***
    is_footer = models.BooleanField(
        "Footer'da Göster", 
        default=False,
        help_text="Footer'da gösterilmesini istediğiniz hizmetleri işaretleyin (max 6 adet)"
    )
    
    # SEO Meta Fields
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    order = models.IntegerField("Sıralama", default=0)
    is_active = models.BooleanField("Aktif", default=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    class Meta:
        verbose_name = "Hizmet"
        verbose_name_plural = "Hizmetler"
        ordering = ['order']

    def clean(self):
        super().clean()
        
        # Footer'da maksimum 6 hizmet kontrolü
        if self.is_footer:
            footer_services = Service.objects.filter(is_footer=True, is_active=True)
            if self.pk:
                footer_services = footer_services.exclude(pk=self.pk)
            if footer_services.count() >= 6:
                raise ValidationError('Footer\'da maksimum 6 hizmet gösterilebilir.')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Slug çakışması kontrolü
        original_slug = self.slug
        counter = 1
        while Service.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('about:service_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class TeamMember(SEOImageMixin, models.Model):
    name = models.CharField("Ad Soyad", max_length=100)
    slug = models.SlugField("SEO URL", max_length=250, unique=True, blank=True,
                           help_text="Otomatik oluşturulur. SEO dostu URL için kullanılır.")
    position = models.CharField("Pozisyon", max_length=100)
    bio = models.TextField("Biyografi", blank=True)
    
    # Cloudinary ile değiştirildi
    image = OptimizedImageField("Orijinal Fotoğraf", folder="team",
                               help_text="Tam boyut orijinal fotoğraf (modal/detay için)")
    
    # Kırpılmış resim alanı
    cropped_image = OptimizedImageField("Kırpılmış Fotoğraf", folder="team/cropped", blank=True,
                                       help_text="Ekip kartlarında gösterilecek kırpılmış fotoğraf")
    
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True,
                               help_text="Ekip üyesi fotoğrafı için SEO alt metni")
    
    # SEO Meta Fields
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    order = models.IntegerField("Sıralama", default=0)
    is_active = models.BooleanField("Aktif", default=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    class Meta:
        verbose_name = "Ekip Üyesi"
        verbose_name_plural = "Ekip Üyeleri"
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Slug çakışması kontrolü
        original_slug = self.slug
        counter = 1
        while TeamMember.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('about:team_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name