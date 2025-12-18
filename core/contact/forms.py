from django import forms
from core.forms import SecureForm
from .models import Contact
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _
import re

class ContactForm(SecureForm, forms.ModelForm):
    captcha = CaptchaField(
        label=_("Güvenlik Kodu"),
        help_text=_("Spam önleme için yukarıdaki kodu girin")
    )
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'\D', '', phone)
            if not re.match(r'^\d{10,11}$', phone):
                raise ValidationError('Geçersiz telefon numarası')
        return phone