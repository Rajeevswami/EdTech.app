from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('lesson', 's3_key', 'file_size', 'duration', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('lesson__title', 's3_key')
    readonly_fields = ('created_at', 'updated_at')
