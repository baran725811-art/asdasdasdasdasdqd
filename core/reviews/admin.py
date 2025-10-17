from django.contrib import admin
# Translation modülünü import et
try:
    from . import translation
except ImportError:
    pass
from .models import Review
from modeltranslation.admin import TranslationAdmin

class ReviewAdmin(TranslationAdmin):
    list_display = ('name', 'rating', 'comment_preview', 'ip_address', 'created_at', 'is_approved', 'has_image')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('name', 'comment', 'ip_address')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    ordering = ('-created_at',)
    
    def comment_preview(self, obj):
        return obj.comment[:100] + "..." if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = "Yorum"
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "Resim"


admin.site.register(Review, ReviewAdmin)