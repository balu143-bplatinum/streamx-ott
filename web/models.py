# web/models.py
from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default="Action")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text="Upload MP4 film file")
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True, help_text="Upload film poster image")
    duration = models.CharField(max_length=20, default="1h 45m")
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def get_video_url(self):
        return self.video_file.url if self.video_file else ""

    @property
    def get_thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=600"


class Advertisement(models.Model):
    title = models.CharField(max_length=100, help_text="Campaign title")
    ad_video = models.FileField(upload_to='ads/', help_text="Upload short MP4 ad video (15-30s)")
    destination_url = models.URLField(blank=True, null=True, help_text="Sponsor link")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Ensure auto_now_add is present

    def __str__(self):
        return self.title


class MidRollAd(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='midroll_ads')
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    timestamp_seconds = models.PositiveIntegerField(
        help_text="Time in SECONDS into the movie when this ad should trigger (e.g. 900 for 15 mins)"
    )

    class Meta:
        ordering = ['timestamp_seconds']

    def __str__(self):
        return f"Ad at {self.timestamp_seconds}s in '{self.video.title}'"


class WatchProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    last_position_seconds = models.FloatField(default=0.0)
    duration_seconds = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')