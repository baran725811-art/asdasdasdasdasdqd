# dashboard/admin.py
from django.contrib import admin
from core.widgets import ReviewCropWidget, MediaCropWidget
from .models import CustomerReview, MediaMention

@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('name', 'review')
    list_editable = ('is_approved',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # CustomerReview için ReviewCropWidget kullan (1:1 - 100x100px)
        for field_name in form.base_fields.keys():
            if 'image' in field_name.lower() or 'photo' in field_name.lower() or 'avatar' in field_name.lower():
                form.base_fields[field_name].widget = ReviewCropWidget()
        return form
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Seçili yorumları onayla"
    
    actions = ['approve_reviews']

@admin.register(MediaMention)
class MediaMentionAdmin(admin.ModelAdmin):
    list_display = ('source', 'title', 'publish_date')
    list_filter = ('publish_date', 'source')
    search_fields = ('title', 'source', 'description')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # MediaMention için MediaCropWidget kullan (8:5 - 400x250px)
        for field_name in form.base_fields.keys():
            if 'image' in field_name.lower() or 'photo' in field_name.lower() or 'logo' in field_name.lower():
                form.base_fields[field_name].widget = MediaCropWidget()
        return form