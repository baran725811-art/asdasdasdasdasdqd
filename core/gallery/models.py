#core\gallery\models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from core.cloudinary_fields import OptimizedImageField, OptimizedVideoField, SEOImageMixin

class Gallery(SEOImageMixin, models.Model):
    MEDIA_TYPES = (
        ('image', 'Resim'),
        ('video', 'Video'),
    )
    
    title = models.CharField("Başlık", max_length=200)
    slug = models.SlugField("SEO URL", max_length=250, unique=True, blank=True,
                           help_text="Otomatik oluşturulur. SEO dostu URL için kullanılır.")
    description = models.TextField("Açıklama", blank=True)
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True,
                            help_text="Görsel için SEO alt metni (max 125 karakter)")
    
    media_type = models.CharField("Medya Tipi", max_length=5, choices=MEDIA_TYPES)
    
    # Cloudinary ile değiştirildi - imagekit kaldırıldı
    from core.cloudinary_fields import RawImageField
    image = RawImageField("Resim", folder="gallery", blank=True)
    
    # kırpma
    cropped_image = OptimizedImageField("Kırpılmış Resim", folder="gallery/cropped", blank=True,
                            help_text="Kartlarda gösterilecek kırpılmış resim")
    
    
    
    
    
    video = OptimizedVideoField("Video Dosyası", folder="gallery/videos", blank=True,
                               help_text="MP4, WebM formatlarını destekler")
    video_url = models.URLField("Video URL", blank=True, help_text="YouTube veya Vimeo URL'si")
    
    # SEO Meta Fields
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    is_featured = models.BooleanField("Öne Çıkan", default=False)
    is_active = models.BooleanField("Aktif", default=True)
    order = models.PositiveIntegerField("Sıralama", default=0)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    class Meta:
        verbose_name = "Galeri"
        verbose_name_plural = "Galeri"
        ordering = ['order', '-created_at']

    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Slug çakışması kontrolü
        original_slug = self.slug
        counter = 1
        while Gallery.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('gallery:detail', kwargs={'slug': self.slug})

    def get_media_url(self):
        """Medya URL'ini döndürür (resim veya video)"""
        if self.media_type == 'image' and self.image:
            return self.image.url
        elif self.media_type == 'video':
            if self.video:
                return self.video.url
            elif self.video_url:
                return self.video_url
        return None

    def is_youtube_video(self):
        """YouTube videosu mu kontrol eder"""
        return self.video_url and ('youtube.com' in self.video_url or 'youtu.be' in self.video_url)

    def is_vimeo_video(self):
        """Vimeo videosu mu kontrol eder"""
        return self.video_url and 'vimeo.com' in self.video_url

    def get_youtube_embed_url(self):
        """YouTube embed URL'ini döndürür"""
        if not self.is_youtube_video():
            return None
        
        video_id = None
        if 'youtube.com/watch?v=' in self.video_url:
            video_id = self.video_url.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in self.video_url:
            video_id = self.video_url.split('youtu.be/')[1].split('?')[0]
        
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    def get_vimeo_embed_url(self):
        """Vimeo embed URL'ini döndürür"""
        if not self.is_vimeo_video():
            return None
        
        video_id = self.video_url.split('vimeo.com/')[-1].split('?')[0]
        return f"https://player.vimeo.com/video/{video_id}"

    def __str__(self):
        return self.title