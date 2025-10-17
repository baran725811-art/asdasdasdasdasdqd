# about/translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import About, Service, TeamMember

class AboutTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'mission', 'vision', 'story', 'meta_title', 'meta_description')

class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

class TeamMemberTranslationOptions(TranslationOptions):
    fields = ( 'position', 'bio')

translator.register(About, AboutTranslationOptions)
translator.register(Service, ServiceTranslationOptions)
translator.register(TeamMember, TeamMemberTranslationOptions)