#core\products\models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from core.cloudinary_fields import OptimizedImageField, SEOImageMixin
import string
import random
from core.cloudinary_fields import RawImageField  # Import ekle

class Category(models.Model):
    name = models.CharField("Kategori Adı", max_length=100)
    slug = models.SlugField("URL", max_length=150, unique=True, blank=True,
                           help_text="Otomatik oluşturulur. SEO dostu URL için kullanılır.")
    description = models.TextField("Açıklama", blank=True)
    
    # Cloudinary ile kategori görseli
    image = OptimizedImageField("Kategori Görseli", folder="categories", blank=True,
                               help_text="Kategori için görsel")
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True,
                               help_text="Kategori görseli için SEO alt metni")
    
    # SEO Meta Fields - Daha uygun karakter limitleri
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    is_active = models.BooleanField("Aktif", default=True)
    order = models.PositiveIntegerField("Sıralama", default=0, 
                                       help_text="Küçük sayı önce görünür")
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Slug çakışması kontrolü
        original_slug = self.slug
        counter = 1
        while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    def get_product_count(self):
        """Bu kategorideki aktif ürün sayısını döndürür"""
        return self.product_set.filter(is_active=True).count()

    def __str__(self):
        return self.name

class Product(SEOImageMixin, models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Kategori")
    name = models.CharField("Ürün Adı", max_length=200)
    slug = models.SlugField("URL", unique=True, max_length=250, blank=True,
                           help_text="Otomatik oluşturulur. SEO dostu URL için kullanılır.")
    
    description = models.TextField("Açıklama", blank=True)
    short_description = models.CharField("Kısa Açıklama", max_length=300, blank=True,
                                       help_text="Ürün listesinde görünecek kısa açıklama")
    
    # Fiyat ve stok alanları
    price = models.DecimalField("Fiyat", max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField("İndirimli Fiyat", max_digits=10, decimal_places=2, 
                                       null=True, blank=True,
                                       help_text="İndirim varsa bu alanı doldurun")
    stock = models.PositiveIntegerField("Stok", null=True, blank=True)
    
    # Cloudinary ile değiştirildi
    image = RawImageField("Orijinal Resim", folder="products", blank=True,
                         help_text="Ürün için tam boyut orijinal resim (modal/detay için)")
    
    # Kırpılmış resim alanı
    cropped_image = OptimizedImageField("Kırpılmış Resim", folder="products/cropped", blank=True,
                                       help_text="Ürün kartlarında gösterilecek kırpılmış resim")
    
    alt_text = models.CharField("Alt Metin (SEO)", max_length=125, blank=True,
                               help_text="Ürün görseli için SEO alt metni")
    
    # Ek ürün bilgileri
    sku = models.CharField("Ürün Kodu", max_length=50, blank=True, null=True, unique=True,
                          help_text="Stok takip kodu - Otomatik oluşturulur")
    brand = models.CharField("Marka", max_length=100, blank=True)
    weight = models.DecimalField("Ağırlık (kg)", max_digits=6, decimal_places=2, 
                               null=True, blank=True)
    
    # SEO Meta Fields - Daha uygun karakter limitleri
    meta_title = models.CharField("Meta Başlık", max_length=60, blank=True,
                                 help_text="Arama motorları için başlık (max 60 karakter)")
    meta_description = models.TextField("Meta Açıklama", max_length=160, blank=True,
                                      help_text="Arama motorları için açıklama (max 160 karakter)")
    
    is_active = models.BooleanField("Satışta", default=True)
    is_featured = models.BooleanField("Öne Çıkan", default=False)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['-created_at']

    def generate_sku(self):
        """Otomatik SKU oluştur: KAT-PRD-1234 formatında"""
        # Kategori kodunu al (ilk 3 harf)
        if self.category:
            category_code = ''.join(c for c in self.category.name if c.isalnum())[:3].upper()
            if not category_code:  # Eğer kategori adında geçerli karakter yoksa
                category_code = 'KAT'
        else:
            category_code = 'PRD'
        
        # Ürün adından kod al (ilk 3 harf/rakam)
        product_name_clean = ''.join(c for c in self.name if c.isalnum())
        product_code = product_name_clean[:3].upper() if product_name_clean else 'UNK'
        
        # 4 haneli rastgele sayı
        random_num = ''.join(random.choices(string.digits, k=4))
        
        # SKU formatı: KAT-PRD-1234
        sku = f"{category_code}-{product_code}-{random_num}"
        
        # Eğer bu SKU varsa, yenisini oluştur
        max_attempts = 50  # Sonsuz döngü koruması
        attempts = 0
        
        while Product.objects.filter(sku=sku).exists() and attempts < max_attempts:
            random_num = ''.join(random.choices(string.digits, k=4))
            sku = f"{category_code}-{product_code}-{random_num}"
            attempts += 1
        
        return sku

    def save(self, *args, **kwargs):
        # Slug oluştur
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Slug çakışması kontrolü
        original_slug = self.slug
        counter = 1
        while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        # SKU oluştur (sadece yeni kayıtlarda veya SKU boşsa)
        if not self.sku:
            self.sku = self.generate_sku()
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    def get_price_display(self):
        """Fiyat görüntüleme için yardımcı method"""
        if self.discount_price:
            return f"{self.discount_price} ₺"
        elif self.price:
            return f"{self.price} ₺"
        return "Fiyat belirtilmemiş"
    
    def get_original_price_display(self):
        """Orijinal fiyat görüntüleme (indirim varsa)"""
        if self.discount_price and self.price:
            return f"{self.price} ₺"
        return None
    
    def has_discount(self):
        """İndirim var mı kontrolü"""
        return self.discount_price and self.price and self.discount_price < self.price
    
    def get_discount_percentage(self):
        """İndirim yüzdesini hesapla"""
        if self.has_discount():
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount, 0)
        return 0
    
    def get_stock_display(self):
        """Stok görüntüleme için yardımcı method"""
        if self.stock is not None:
            if self.stock > 0:
                return f"{self.stock} adet"
            else:
                return "Stokta yok"
        return "Stok belirtilmemiş"
    
    def is_in_stock(self):
        """Stokta var mı kontrolü"""
        return self.stock is None or self.stock > 0

    def __str__(self):
        return self.name