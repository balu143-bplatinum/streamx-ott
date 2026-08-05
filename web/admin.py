from django.contrib import admin
from django.utils.html import format_html
from .models import Video, Advertisement, MidRollAd, WatchProgress

class MidRollAdInline(admin.TabularInline):
    model = MidRollAd
    extra = 1
    verbose_name = "Scheduled Ad Break"
    verbose_name_plural = "Scheduled Mid-Roll Ad Breaks"

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('preview_thumbnail', 'title', 'category', 'duration', 'views_count', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'category')
    inlines = [MidRollAdInline]

    def preview_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 6px;" />', obj.thumbnail.url)
        return "No Poster"

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'destination_url')

@admin.register(WatchProgress)
class WatchProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'last_position_seconds', 'is_completed')