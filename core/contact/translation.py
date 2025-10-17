# contact/translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import Contact

class ContactTranslationOptions(TranslationOptions):
    fields = ('subject', 'message')

translator.register(Contact, ContactTranslationOptions)