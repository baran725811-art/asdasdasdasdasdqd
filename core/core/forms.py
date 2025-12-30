# core/forms.py
from django import forms
from django.core.exceptions import ValidationError
import bleach
import re
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _



class SecureForm(forms.Form):    
    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                # HTML temizleme
                cleaned_data[field] = bleach.clean(
                    value,
                    tags=[],  # İzin verilen HTML etiketleri
                    attributes={},  # İzin verilen HTML özellikleri
                    strip=True
                )
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Email doğrulama
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('Geçersiz email adresi')
        return email
