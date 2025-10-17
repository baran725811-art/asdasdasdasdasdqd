# core/validators.py - YENİ DOSYA OLUŞTUR

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Özel güçlü parola doğrulayıcısı
    """
    def validate(self, password, user=None):
        errors = []
        
        # En az bir büyük harf
        if not re.search(r'[A-Z]', password):
            errors.append(_('Parola en az bir büyük harf içermelidir.'))
        
        # En az bir küçük harf
        if not re.search(r'[a-z]', password):
            errors.append(_('Parola en az bir küçük harf içermelidir.'))
        
        # En az bir rakam
        if not re.search(r'[0-9]', password):
            errors.append(_('Parola en az bir rakam içermelidir.'))
        
        # En az bir özel karakter
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(_('Parola en az bir özel karakter (!@#$%^&* vb.) içermelidir.'))
        
        # Yaygın zayıf parolalar
        weak_passwords = [
            'password', '123456', 'qwerty', 'abc123', 
            'password123', 'admin', 'letmein', 'welcome'
        ]
        if password.lower() in weak_passwords:
            errors.append(_('Bu parola çok yaygın kullanılan zayıf bir paroladır.'))
        
        # Tekrarlayan karakterler (3'ten fazla)
        if re.search(r'(.)\1{2,}', password):
            errors.append(_('Parola 3\'ten fazla tekrarlayan karakter içeremez.'))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            'Parolanız en az 12 karakter uzunluğunda olmalı ve '
            'büyük harf, küçük harf, rakam ve özel karakter içermelidir.'
        )