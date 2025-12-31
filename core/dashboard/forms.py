# dashboard/forms.py
from captcha.fields import CaptchaField
from django.contrib.auth import authenticate
from axes.helpers import get_failure_limit
from django import forms 
from django_ckeditor_5.widgets import CKEditor5Widget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from about.models import About, Service, TeamMember
from gallery.models import Gallery
from products.models import Category, Product
from home.models import CarouselSlide
from .models import MediaMention, CustomerReview

from .mixins import BaseTranslationForm, TranslationFieldGenerator
from .constants import FORM_WIDGET_CLASSES, LANGUAGE_NAMES
from django.contrib.auth.forms import PasswordChangeForm
from core.models import SiteSettings


from .models import DashboardTranslationSettings
from .constants import LANGUAGE_CHOICES, LANGUAGE_NAMES

# =============================================================================
# CAPTCHA destekli login formu  
# =============================================================================

from django import forms
from django.contrib.auth import authenticate
from captcha.fields import CaptchaField

class DashboardLoginForm(forms.Form):
    username = forms.CharField(
        label='Kullanıcı Adı',
        widget=forms.TextInput(attrs={
            'class': 'form-control-modern',
            'placeholder': 'Kullanıcı adınızı girin',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label='Parola',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-modern',
            'placeholder': 'Parolanızı girin',
            'autocomplete': 'current-password'
        })
    )
    captcha = CaptchaField(
        label='Güvenlik Kodu',
        help_text='Yukarıdaki matematik işleminin sonucunu yazın',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(*args, **kwargs)
        
        # CAPTCHA widget'ına CSS class ekle
        if 'captcha' in self.fields:
            # TextInput kısmına class ekle
            self.fields['captcha'].widget.widgets[1].attrs.update({
                'class': 'form-control-modern',
                'placeholder': 'Sonucu yazın'
            })
        
        # CAPTCHA'yı koşullu olarak zorunlu yap
        if self.show_captcha:
            if 'captcha' in self.fields:
                self.fields['captcha'].required = True
        else:
            if 'captcha' in self.fields:
                self.fields['captcha'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            user = authenticate(
                request=self.request,
                username=username, 
                password=password
            )
            if user is None:
                raise forms.ValidationError('Kullanıcı adı veya parola hatalı.')
            elif not user.is_staff:
                raise forms.ValidationError('Bu hesapla dashboard\'a erişim yetkiniz yok.')
            elif not user.is_active:
                raise forms.ValidationError('Hesabınız devre dışı bırakılmış.')
            
            cleaned_data['user'] = user
        
        return cleaned_data
# =============================================================================
# TRANSLATION FORMS - Optimize edilmiş çeviri destekli formlar
# =============================================================================

class AboutForm(forms.ModelForm):
    """Hakkımızda formu - DÜZELTILMIŞ VERSİYON"""
    
    mission = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False, 
        label="Misyonumuz"
    )
    vision = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False, 
        label="Vizyonumuz"
    )
    story = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False, 
        label="Hikayemiz"
    )
    
    class Meta:
        model = About
        fields = ['title', 'short_description', 'mission', 'vision', 
                 'story', 'image', 'years_experience', 'completed_jobs', 
                 'happy_customers', 'total_services', 'customer_satisfaction',
                 'meta_title', 'meta_description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sayfa başlığı'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'years_experience': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'id': 'id_years_experience',
                'name': 'years_experience'
            }),
            'completed_jobs': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0,
                'id': 'id_completed_jobs', 
                'name': 'completed_jobs'
            }),
            'happy_customers': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0,
                'id': 'id_happy_customers',
                'name': 'happy_customers'
            }),
            'total_services': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0,
                'id': 'id_total_services',
                'name': 'total_services'
            }),
            'customer_satisfaction': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'max': 100,
                'id': 'id_customer_satisfaction',
                'name': 'customer_satisfaction'
            }),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        # Çeviri parametrelerini temizle
        kwargs.pop('translation_enabled', None)
        kwargs.pop('enabled_languages', None)
        kwargs.pop('user', None)
        
        super().__init__(*args, **kwargs)
        
        # Tüm alanları opsiyonel yap (title hariç)
        for field_name, field in self.fields.items():
            if field_name != 'title':
                field.required = False

# dashboard/forms.py - MediaMentionFormWithTranslation sınıfını tamamen değiştirin

class MediaMentionFormWithTranslation(BaseTranslationForm):
    """Basın haberleri formu - KESIN ÇÖZÜM"""
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'title_{lang_code}',
                        f'source_{lang_code}',
                        f'description_{lang_code}'
                    ])
            
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
        
        # ✅ KRİTİK: Edit modunda initial değerleri set et
        if hasattr(self, 'instance') and self.instance and self.instance.pk:
            
            # URL field'ını zorla set et
            if 'url' in self.fields:
                self.fields['url'].initial = self.instance.url
                if hasattr(self, 'initial'):
                    self.initial['url'] = self.instance.url
                else:
                    self.initial = {'url': self.instance.url}
            
            # Publish date field'ını zorla set et  
            if 'publish_date' in self.fields:
                self.fields['publish_date'].initial = self.instance.publish_date
                if hasattr(self, 'initial'):
                    self.initial['publish_date'] = self.instance.publish_date
                else:
                    self.initial = self.initial or {}
                    self.initial['publish_date'] = self.instance.publish_date
        
        # Tüm alanları opsiyonel yap (title ve source hariç)
        for field_name, field in self.fields.items():
            if field_name not in ['title', 'source']:
                field.required = False
        
        # Çeviri alanları ekle
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = MediaMention
        fields = ['title', 'source', 'url', 'publish_date', 'description', 
                 'image', 'is_active', 'order', 'alt_text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Haber başlığı',
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Kaynak adı',
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://example.com/haber-linki'
            }),
            'publish_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Haberin kısa özeti'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0,
                'value': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Görsel için SEO alt metni'
            }),
        }
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle"""
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                # Title alanı - Edit modunda initial değer
                title_initial = ''
                if hasattr(self, 'instance') and self.instance.pk:
                    title_initial = getattr(self.instance, f'title_{lang_code}', '') or ''
                
                self.fields[f'title_{lang_code}'] = forms.CharField(
                    label=f'Haber Başlığı ({lang_name})',
                    required=True,
                    initial=title_initial,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Haber Başlığı ({lang_name}) - Zorunlu'
                    })
                )
                
                # Source alanı - Edit modunda initial değer
                source_initial = ''
                if hasattr(self, 'instance') and self.instance.pk:
                    source_initial = getattr(self.instance, f'source_{lang_code}', '') or ''
                
                self.fields[f'source_{lang_code}'] = forms.CharField(
                    label=f'Kaynak ({lang_name})',
                    required=True,
                    initial=source_initial,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Kaynak ({lang_name}) - Zorunlu'
                    })
                )
                
                # Description alanı - Edit modunda initial değer
                desc_initial = ''
                if hasattr(self, 'instance') and self.instance.pk:
                    desc_initial = getattr(self.instance, f'description_{lang_code}', '') or ''
                
                self.fields[f'description_{lang_code}'] = forms.CharField(
                    label=f'Açıklama ({lang_name})',
                    required=True,
                    initial=desc_initial,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'] + ' required-translation',
                        'placeholder': f'Açıklama ({lang_name}) - Zorunlu',
                        'rows': 4
                    })
                )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Boş alanlar için varsayılan değerler
        if not instance.order:
            instance.order = 0
            
        if commit:
            instance.save()
        
        return instance
    
    
class CategoryFormWithTranslation(BaseTranslationForm):
    """Kategori formu - SLUG SORUNU ÇÖZÜLDÜ"""
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle - BU ÖNEMLİ!
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'name_{lang_code}',
                        f'description_{lang_code}'
                    ])
            
            # Meta fields'ı dinamik olarak genişlet
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
    
        # ★ BU SATIRI EKLE:
        if 'slug' in self.fields:
            self.fields['slug'].required = False
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'meta_title', 'meta_description', 'is_active']
        widgets = {
            'name': forms.TextInput(),
            'slug': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 4}),
            'meta_title': forms.TextInput(),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle - Gallery gibi"""        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                # Name alanı
                self.fields[f'name_{lang_code}'] = forms.CharField(
                    label=f'Kategori Adı ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Kategori Adı ({lang_name}) - Zorunlu'
                    })
                )
                
                # Description alanı
                self.fields[f'description_{lang_code}'] = forms.CharField(
                    label=f'Kategori Açıklaması ({lang_name})',
                    required=True,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'] + ' required-translation',
                        'placeholder': f'Kategori Açıklaması ({lang_name}) - Zorunlu',
                        'rows': 4
                    })
                )

    def save(self, commit=True):
        """Otomatik slug oluşturma"""
        instance = super().save(commit=False)
        
        # Slug boşsa otomatik oluştur
        if not instance.slug:
            from django.utils.text import slugify
            instance.slug = slugify(instance.name)
            
            # Eğer aynı slug varsa sayı ekle
            original_slug = instance.slug
            counter = 1
            while Category.objects.filter(slug=instance.slug).exclude(pk=instance.pk).exists():
                instance.slug = f"{original_slug}-{counter}"
                counter += 1
        
        if commit:
            instance.save()
        
        return instance


class ProductFormWithTranslation(BaseTranslationForm):
    """Ürün formu - SLUG SORUNU ÇÖZÜLDÜ"""
    
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False,
        label="Ürün Açıklaması"
    )
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle - BU ÖNEMLİ!
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'name_{lang_code}',
                        f'description_{lang_code}',
                        f'meta_title_{lang_code}',
                        f'meta_description_{lang_code}'
                    ])
            
            # Meta fields'ı dinamik olarak genişlet
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
        
        # ★ SLUG'I İSTEĞE BAĞLI YAP - CATEGORY GİBİ
        if 'slug' in self.fields:
            self.fields['slug'].required = False
        
        # Fiyat ve stok isteğe bağlı
        self.fields['price'].required = False
        self.fields['stock'].required = False
        self.fields['description'].required = False
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 
                 'stock', 'image', 'cropped_image',  # ← EKLE
                 'meta_title', 'meta_description', 
                 'is_featured', 'is_active']
        widgets = {
            'name': forms.TextInput(),
            'slug': forms.TextInput(),
            'meta_title': forms.TextInput(),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock': forms.NumberInput(),
        }
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle - Gallery gibi"""        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                # Name alanı
                self.fields[f'name_{lang_code}'] = forms.CharField(
                    label=f'Ürün Adı ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Ürün Adı ({lang_name}) - Zorunlu'
                    })
                )
                
                # Description alanı
                self.fields[f'description_{lang_code}'] = forms.CharField(
                    label=f'Ürün Açıklaması ({lang_name})',
                    required=True,
                    widget=CKEditor5Widget(config_name='default')
                )
                
                # Meta title alanı
                self.fields[f'meta_title_{lang_code}'] = forms.CharField(
                    label=f'Meta Başlık ({lang_name})',
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'],
                        'placeholder': f'Meta Başlık ({lang_name})'
                    })
                )
                
                # Meta description alanı
                self.fields[f'meta_description_{lang_code}'] = forms.CharField(
                    label=f'Meta Açıklama ({lang_name})',
                    required=False,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'],
                        'placeholder': f'Meta Açıklama ({lang_name})',
                        'rows': 2
                    })
                )

    def save(self, commit=True):
        """Otomatik slug oluşturma"""
        instance = super().save(commit=False)
        
        # Slug boşsa otomatik oluştur
        if not instance.slug:
            from django.utils.text import slugify
            instance.slug = slugify(instance.name)
            
            # Eğer aynı slug varsa sayı ekle
            original_slug = instance.slug
            counter = 1
            while Product.objects.filter(slug=instance.slug).exclude(pk=instance.pk).exists():
                instance.slug = f"{original_slug}-{counter}"
                counter += 1
        
        if commit:
            instance.save()
        
        return instance

# dashboard/forms.py - GalleryFormWithTranslation DÜZELTME

class GalleryFormWithTranslation(BaseTranslationForm):
    """Galeri formu - KIRPMA DESTEKLİ"""
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'title_{lang_code}',
                        f'description_{lang_code}', 
                        f'alt_text_{lang_code}'
                    ])
            
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = Gallery
        fields = [
            'title', 'description', 'alt_text', 'media_type', 
            'image',  # ← Orijinal/kırpılmamış görsel
            'video_url', 'is_active', 'is_featured', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Galeri başlığı'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO alt metni'
            }),
            'media_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control image-crop-input',
                'accept': 'image/*',
                'data-crop-type': 'gallery',  # ← Kırpma tipi
                'data-crop-width': '800',
                'data-crop-height': '600',
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),

        }
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle"""        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                # Title alanı
                self.fields[f'title_{lang_code}'] = forms.CharField(
                    label=f'Başlık ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Başlık ({lang_name}) - Zorunlu'
                    })
                )
                
                # Description alanı
                self.fields[f'description_{lang_code}'] = forms.CharField(
                    label=f'Açıklama ({lang_name})',
                    required=True,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'] + ' required-translation',
                        'placeholder': f'Açıklama ({lang_name}) - Zorunlu',
                        'rows': 4
                    })
                )
                
                # Alt text alanı
                self.fields[f'alt_text_{lang_code}'] = forms.CharField(
                    label=f'Alt Metin ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Alt Metin ({lang_name}) - Zorunlu'
                    })
                )
    
    def save(self, commit=True):
        """Kırpılmış görseli otomatik kaydet"""
        instance = super().save(commit=False)
        
        # ★ KRİTİK: Kırpılmış görsel verisini al
        if hasattr(self, 'cleaned_data'):
            cropped_data = self.cleaned_data.get('cropped_image_data')
            if cropped_data:
                # Kırpılmış görseli kaydet
                from django.core.files.base import ContentFile
                import base64
                
                # Base64'ü decode et
                format, imgstr = cropped_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Dosya oluştur
                image_data = ContentFile(base64.b64decode(imgstr))
                file_name = f'gallery_cropped_{instance.id}.{ext}'
                
                # cropped_image field'ına kaydet
                instance.cropped_image.save(file_name, image_data, save=False)
        
        if commit:
            instance.save()
        
        return instance
                
class CarouselSlideFormWithTranslation(BaseTranslationForm):
    """Carousel slayt formu - DÜZELTILMIŞ"""
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle - BU ÖNEMLİ!
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'title_{lang_code}',
                        f'description_{lang_code}',
                        f'alt_text_{lang_code}',
                        f'button_text_{lang_code}'
                    ])
            
            # Meta fields'ı dinamik olarak genişlet
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
        
        # Alt text için help text
        self.fields['alt_text'].help_text = 'SEO için önemli! Görseli açıklayan kısa metin. (Max 125 karakter)'
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = CarouselSlide
        fields = ['title', 'description', 'alt_text', 'image', 'button_text', 'button_url', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
            'alt_text': forms.TextInput(attrs={
                'maxlength': '125',
                'placeholder': 'Görsel için SEO açıklaması (Max 125 karakter)'
            }),
            'button_text': forms.TextInput(),
            'button_url': forms.TextInput(),
            'order': forms.NumberInput(attrs={'value': 0, 'min': 0}),  # ✅ Varsayılan değer
        }
    
    def clean_order(self):
        """Order alanını temizle ve varsayılan değer ata"""
        order = self.cleaned_data.get('order')
        
        # Boş, None veya geçersiz değerleri 0 yap
        if not order or order == '' or order is None:
            return 0
        
        try:
            return int(order)
        except (ValueError, TypeError):
            return 0
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle - Gallery gibi"""        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                # Title alanı
                self.fields[f'title_{lang_code}'] = forms.CharField(
                    label=f'Başlık ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Başlık ({lang_name}) - Zorunlu'
                    })
                )
                
                # Description alanı
                self.fields[f'description_{lang_code}'] = forms.CharField(
                    label=f'Açıklama ({lang_name})',
                    required=True,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'] + ' required-translation',
                        'placeholder': f'Açıklama ({lang_name}) - Zorunlu',
                        'rows': 3
                    })
                )
                
                # Alt text alanı
                self.fields[f'alt_text_{lang_code}'] = forms.CharField(
                    label=f'Alt Metin (SEO) ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Alt Metin ({lang_name}) - Zorunlu',
                        'maxlength': '125'
                    })
                )
                
                # Button text alanı
                self.fields[f'button_text_{lang_code}'] = forms.CharField(
                    label=f'Buton Metni ({lang_name})',
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'],
                        'placeholder': f'Buton Metni ({lang_name})'
                    })
                )


class ServiceFormWithTranslation(BaseTranslationForm):
    """Hizmet formu - KESIN ÇÖZÜM - Gallery gibi"""
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle - BU ÖNEMLİ!
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'title_{lang_code}',
                        f'description_{lang_code}'
                    ])
            
            # Meta fields'ı dinamik olarak genişlet
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = Service
        fields = ['title', 'description', 'image', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 4}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),

        }
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle - Gallery gibi"""        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                # Edit modunda mevcut değerleri al
                title_initial = ''
                desc_initial = ''
                if hasattr(self, 'instance') and self.instance.pk:
                    title_initial = getattr(self.instance, f'title_{lang_code}', '') or ''
                    desc_initial = getattr(self.instance, f'description_{lang_code}', '') or ''
                
                # Title alanı
                self.fields[f'title_{lang_code}'] = forms.CharField(
                    label=f'Hizmet Başlığı ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Hizmet Başlığı ({lang_name}) - Zorunlu'
                    })
                )
                
                # Description alanı
                self.fields[f'description_{lang_code}'] = forms.CharField(
                    label=f'Hizmet Açıklaması ({lang_name})',
                    required=True,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'] + ' required-translation',
                        'placeholder': f'Hizmet Açıklaması ({lang_name}) - Zorunlu',
                        'rows': 4
                    })
                )

class TeamMemberFormWithTranslation(BaseTranslationForm):
    """Takım üyesi formu - DÜZELTILMIŞ"""
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle - BU ÖNEMLİ!
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'position_{lang_code}',
                        f'bio_{lang_code}'
                    ])
            
            # Meta fields'ı dinamik olarak genişlet
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = TeamMember
        fields = ['name', 'position', 'bio', 'image', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(),
            'position': forms.TextInput(),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 0
            }),

            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle"""        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                
                
                # Position alanı
                self.fields[f'position_{lang_code}'] = forms.CharField(
                    label=f'Pozisyon ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Pozisyon ({lang_name}) - Zorunlu'
                    })
                )
                
                # Bio alanı
                self.fields[f'bio_{lang_code}'] = forms.CharField(
                    label=f'Biyografi ({lang_name})',
                    required=True,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'] + ' required-translation',
                        'placeholder': f'Biyografi ({lang_name}) - Zorunlu',
                        'rows': 4
                    })
                )


# =============================================================================
# LEGACY FORMS - Çeviri desteksiz eski formlar (backward compatibility)
# =============================================================================

class MediaMentionForm(forms.ModelForm):
    class Meta:
        model = MediaMention
        fields = ['title', 'source', 'url', 'publish_date', 'description', 
                 'image', 'is_active', 'order']
        widgets = {
            'publish_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'meta_title', 
                 'meta_description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }


class ProductForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False,
        label="Ürün Açıklaması"
    )
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 
                 'stock', 'image', 'meta_title', 'meta_description', 
                 'is_featured', 'is_active']
        widgets = {
            'meta_description': forms.Textarea(attrs={'rows': 2}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'İsteğe bağlı'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'İsteğe bağlı'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fiyat ve stok alanlarını isteğe bağlı yap
        self.fields['price'].required = False
        self.fields['stock'].required = False
        self.fields['meta_title'].required = False
        self.fields['meta_description'].required = False
        self.fields['description'].required = False


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'description', 'media_type', 'image', 'video_url', 'is_active', 'is_featured', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'media_type': forms.Select(
                choices=[('image', 'Resim'), ('video', 'Video')],
                attrs={'class': 'form-control', 'id': 'id_media_type'}
            ),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube veya Vimeo URL'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomerReviewForm(forms.ModelForm):
    class Meta:
        model = CustomerReview
        fields = ['name', 'review', 'rating', 'is_approved']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class CarouselSlideForm(forms.ModelForm):
    class Meta:
        model = CarouselSlide
        fields = ['title', 'description', 'image', 'button_text', 
                 'button_url', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'position', 'bio', 'image', 'order', 'is_active']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'image', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# =============================================================================
# USER MANAGEMENT FORMS
# =============================================================================

class CustomUserCreationForm(UserCreationForm):
    """Dashboard için özel kullanıcı oluşturma formu"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Alan etiketlerini Türkçe yap
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['first_name'].label = 'Ad'
        self.fields['last_name'].label = 'Soyad'
        self.fields['email'].label = 'E-posta'
        self.fields['is_active'].label = 'Aktif'
        self.fields['is_staff'].label = 'Yönetici'
        self.fields['password1'].label = 'Şifre'
        self.fields['password2'].label = 'Şifre Tekrarı'
        
        # Widget'ları güncelle
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})


class CustomUserChangeForm(UserChangeForm):
    """Dashboard için özel kullanıcı düzenleme formu"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Şifre alanını kaldır (ayrı fonksiyon ile yönetilecek)
        if 'password' in self.fields:
            del self.fields['password']
        
        # Alan etiketlerini Türkçe yap
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['first_name'].label = 'Ad'
        self.fields['last_name'].label = 'Soyad'
        self.fields['email'].label = 'E-posta'
        self.fields['is_active'].label = 'Aktif'
        self.fields['is_staff'].label = 'Yönetici'


class UserPasswordChangeForm(forms.Form):
    """Kullanıcı şifre değiştirme formu"""
    new_password = forms.CharField(
        label='Yeni Şifre',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'minlength': '8'}),
        help_text='Şifreniz en az 8 karakter uzunluğunda olmalıdır.'
    )
    confirm_password = forms.CharField(
        label='Şifre Tekrarı',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('Şifreler eşleşmiyor.')
            
            if len(new_password) < 8:
                raise forms.ValidationError('Şifre en az 8 karakter olmalıdır.')
        
        return cleaned_data
    
    

class AboutFormWithTranslation(BaseTranslationForm):
    """Hakkımızda formu - Çeviri destekli"""
    
    mission = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False, 
        label="Misyonumuz"
    )
    vision = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False, 
        label="Vizyonumuz"
    )
    story = forms.CharField(
        widget=CKEditor5Widget(config_name='default'), 
        required=False, 
        label="Hikayemiz"
    )
    
    def __init__(self, *args, **kwargs):
        # Çeviri alanlarını meta fields'a ekle
        if kwargs.get('translation_enabled', False) and len(kwargs.get('enabled_languages', ['tr'])) > 1:
            enabled_languages = kwargs.get('enabled_languages', ['tr'])
            additional_fields = []
            for lang_code in enabled_languages:
                if lang_code != 'tr':
                    additional_fields.extend([
                        f'title_{lang_code}',
                        f'short_description_{lang_code}',
                        f'mission_{lang_code}',
                        f'vision_{lang_code}',
                        f'story_{lang_code}'
                    ])
            
            self._meta.fields = list(self._meta.fields) + additional_fields
        
        super().__init__(*args, **kwargs)
        
        # Tüm alanları opsiyonel yap (title hariç)
        for field_name, field in self.fields.items():
            if field_name != 'title':
                field.required = False
        
        if self.translation_enabled and len(self.enabled_languages) > 1:
            self._add_translation_fields()
    
    class Meta:
        model = About
        fields = ['title', 'short_description', 'mission', 'vision', 
                 'story', 'image', 'years_experience', 'completed_jobs', 
                 'happy_customers', 'total_services', 'customer_satisfaction',
                 'meta_title', 'meta_description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sayfa başlığı'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'completed_jobs': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'happy_customers': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_services': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'customer_satisfaction': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def _add_translation_fields(self):
        """Çeviri alanlarını manuel olarak ekle"""        
        for lang_code in self.enabled_languages:
            if lang_code != 'tr':
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                
                # Title alanı
                self.fields[f'title_{lang_code}'] = forms.CharField(
                    label=f'Sayfa Başlığı ({lang_name})',
                    required=True,
                    widget=forms.TextInput(attrs={
                        'class': FORM_WIDGET_CLASSES['text'] + ' required-translation',
                        'placeholder': f'Sayfa Başlığı ({lang_name}) - Zorunlu'
                    })
                )
                
                # Short description alanı
                self.fields[f'short_description_{lang_code}'] = forms.CharField(
                    label=f'Kısa Açıklama ({lang_name})',
                    required=True,
                    widget=forms.Textarea(attrs={
                        'class': FORM_WIDGET_CLASSES['textarea'] + ' required-translation',
                        'placeholder': f'Kısa Açıklama ({lang_name}) - Zorunlu',
                        'rows': 4
                    })
                )
                
                # Mission, Vision, Story - CKEditor ile
                self.fields[f'mission_{lang_code}'] = forms.CharField(
                    label=f'Misyonumuz ({lang_name})',
                    required=True,
                    widget=CKEditor5Widget(config_name='default')
                )
                
                self.fields[f'vision_{lang_code}'] = forms.CharField(
                    label=f'Vizyonumuz ({lang_name})',
                    required=True,
                    widget=CKEditor5Widget(config_name='default')
                )
                
                self.fields[f'story_{lang_code}'] = forms.CharField(
                    label=f'Hikayemiz ({lang_name})',
                    required=True,
                    widget=CKEditor5Widget(config_name='default')
                )





#profil ve ayarlar bölümü
class ProfileForm(forms.ModelForm):
    """Kullanıcı profil formu"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-posta',
            'username': 'Kullanıcı Adı',
        }

from core.models import SiteSettings  # En üste ekle

class BusinessSettingsForm(forms.ModelForm):
    """Site ayarları formu - SiteSettings kullanarak"""
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'site_tagline', 'site_logo', 'favicon',
            'contact_phone', 'contact_email', 'contact_address',
            'google_maps_embed_url',
            'facebook_url', 'instagram_url', 'twitter_url', 
            'whatsapp_number', 'youtube_url',
            'seo_title', 'seo_description', 'seo_keywords',
            'primary_color', 'secondary_color', 'navbar_color',
            'pdf_catalog_enabled', 'pdf_catalog_file', 'pdf_catalog_title',
            'translation_enabled'
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'site_tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'google_maps_embed_url': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'seo_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'navbar_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'site_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'favicon': forms.FileInput(attrs={'class': 'form-control'}),
            'pdf_catalog_file': forms.FileInput(attrs={'class': 'form-control'}),
            'pdf_catalog_title': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'site_name': 'Site Adı',
            'site_tagline': 'Site Sloganı',
            'contact_phone': 'Telefon',
            'contact_email': 'E-posta',
            'contact_address': 'Adres',
            'google_maps_embed_url': 'Google Maps Embed URL',
            'facebook_url': 'Facebook URL',
            'instagram_url': 'Instagram URL',
            'twitter_url': 'Twitter URL',
            'whatsapp_number': 'WhatsApp Numarası',
            'youtube_url': 'YouTube URL',
            'seo_title': 'SEO Başlık',
            'seo_description': 'SEO Açıklama',
            'seo_keywords': 'SEO Anahtar Kelimeler',
            'primary_color': 'Ana Renk',
            'secondary_color': 'İkincil Renk',
            'navbar_color': 'Navbar Rengi',
            'site_logo': 'Logo',
            'favicon': 'Favicon',
            'pdf_catalog_enabled': 'PDF Katalog Aktif',
            'pdf_catalog_file': 'PDF Katalog Dosyası',
            'pdf_catalog_title': 'PDF Katalog Başlığı',
            'translation_enabled': 'Çeviri Sistemi Aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tüm alanları opsiyonel yap
        for field_name, field in self.fields.items():
            field.required = False

class CustomPasswordChangeForm(PasswordChangeForm):
    """Özelleştirilmiş şifre değiştirme formu"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Türkçe etiketler
        self.fields['old_password'].label = 'Mevcut Şifre'
        self.fields['new_password1'].label = 'Yeni Şifre'
        self.fields['new_password2'].label = 'Yeni Şifre (Tekrar)'
        
        




class DashboardTranslationSettingsForm(forms.ModelForm):
    """Dashboard çeviri ayarları formu"""
    
    class Meta:
        model = DashboardTranslationSettings
        fields = ['dashboard_language', 'primary_language', 'enabled_languages']
        widgets = {
            'dashboard_language': forms.Select(
                choices=LANGUAGE_CHOICES,
                attrs={
                    'class': 'form-select',
                    'id': 'id_dashboard_language'
                }
            ),
            'primary_language': forms.Select(
                choices=LANGUAGE_CHOICES,
                attrs={
                    'class': 'form-select',
                    'id': 'id_primary_language'
                }
            ),
        }
        labels = {
            'dashboard_language': 'Dashboard Arayüz Dili',
            'primary_language': 'Site Ana Dili',
            'enabled_languages': 'Ek Çeviri Dilleri',
        }
        help_texts = {
            'dashboard_language': 'Sadece dashboard arayüzünün görüntüleneceği dil',
            'primary_language': 'Site içeriği için ana dil (her zaman dahil olur)',
            'enabled_languages': 'Site için aktif olan tüm diller',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dashboard dili seçeneklerini ayarla
        dashboard_choices = [
            ('tr', '🇹🇷 Türkçe'),
            ('en', '🇺🇸 İngilizce'),
            ('de', '🇩🇪 Almanca'),
            ('fr', '🇫🇷 Fransızca'),
            ('es', '🇪🇸 İspanyolca'),
            ('ru', '🇷🇺 Rusça'),
            ('ar', '🇸🇦 Arapça'),
        ]
        
        primary_choices = [
            ('tr', '🌟 🇹🇷 Türkçe'),
            ('en', '🌟 🇺🇸 İngilizce'), 
            ('de', '🌟 🇩🇪 Almanca'),
            ('fr', '🌟 🇫🇷 Fransızca'),
            ('es', '🌟 🇪🇸 İspanyolca'),
            ('ru', '🌟 🇷🇺 Rusça'),
            ('ar', '🌟 🇸🇦 Arapça'),
        ]
        
        self.fields['dashboard_language'].choices = dashboard_choices
        self.fields['primary_language'].choices = primary_choices