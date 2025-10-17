# home/translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import CarouselSlide

class CarouselSlideTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'alt_text', 'button_text')

translator.register(CarouselSlide, CarouselSlideTranslationOptions)