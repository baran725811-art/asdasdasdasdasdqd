# contact/admin.py
from django.contrib import admin

# Translation modülünü import et
try:
    from . import translation
except ImportError:
    pass

from .models import Contact
from modeltranslation.admin import TranslationAdmin

class ContactAdmin(TranslationAdmin):
    list_display = ['name', 'email', 'subject', 'ip_address', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message', 'ip_address']
    readonly_fields = ['created_at', 'ip_address']
    list_editable = ['is_read']

admin.site.register(Contact, ContactAdmin)