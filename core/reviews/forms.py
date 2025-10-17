from django import forms
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _
from .models import Review

class ReviewForm(forms.ModelForm):
    captcha = CaptchaField(
        label=_("Güvenlik Kodu"),
        help_text=_("Spam önleme için yukarıdaki kodu girin")
    )
    
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adınız Soyadınız'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5',
                'placeholder': 'Puanınız (1-5 arası)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Yorumunuz'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/gif'
            })
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise ValidationError('Puan 1-5 arasında olmalıdır.')
        return rating

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 10:
            raise ValidationError('Yorum en az 10 karakter olmalıdır.')
        return comment

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Dosya boyutu kontrolü (2MB sınırı)
            if image.size > 2 * 1024 * 1024:
                raise ValidationError('Dosya boyutu 2MB\'dan büyük olamaz.')
            # Dosya türü kontrolü
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if image.content_type not in allowed_types:
                raise ValidationError('Yalnızca JPEG, PNG veya GIF dosyaları yüklenebilir.')
        return image