# gallery/translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import Gallery

class GalleryTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'alt_text')  # alt_text eklendi

translator.register(Gallery, GalleryTranslationOptions)