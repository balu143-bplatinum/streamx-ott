from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from cloudinary_storage.storage import VideoMediaCloudinaryStorage

class Video(models.Model):
    CATEGORY_CHOICES = [
        ('Action', 'Action'),
        ('Comedy', 'Comedy'),
        ('Drama', 'Drama'),
        ('Horror', 'Horror'),
        ('Sci-Fi', 'Sci-Fi'),
        ('Romance', 'Romance'),
        ('Thriller', 'Thriller'),
        ('Documentary', 'Documentary'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Action')
    
    # Direct File Upload (MP4, MKV, AVI, MOV, WEBM)
    video_file = models.FileField(
        upload_to='videos/',
        storage=VideoMediaCloudinaryStorage(),
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'avi', 'mov', 'webm'])],
        help_text="Upload video file (MP4, MKV, AVI, MOV, WEBM)"
    )
    
    # External Direct Stream/CDN Link
    external_video_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Optional: Paste direct video link if not uploading a file"
    )

    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    duration = models.CharField(max_length=20, default="1h 45m")
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def get_video_url(self):
        if self.video_file:
            return self.video_file.url
        elif self.external_video_url:
            return self.external_video_url
        return ""


class Advertisement(models.Model):
    """Global Video Ads Repository."""
    title = models.CharField(max_length=200)
    ad_video_file = models.FileField(
        upload_to='ads/',
        storage=VideoMediaCloudinaryStorage(),
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'webm'])]
    )
    external_ad_url = models.URLField(max_length=1000, blank=True, null=True)
    destination_url = models.URLField(max_length=1000, default="https://google.com")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def get_ad_url(self):
        if self.ad_video_file:
            return self.ad_video_file.url
        return self.external_ad_url or ""


class MidRollAd(models.Model):
    """Schedules an Advertisement break for a specific Video timestamp."""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='midroll_ads')
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    time_in_seconds = models.PositiveIntegerField(
        default=0, 
        help_text="Timestamp in seconds to trigger ad (e.g., 300 = 5 minutes mark)"
    )

    def __str__(self):
        return f"{self.ad.title} at {self.time_in_seconds}s on {self.video.title}"


class WatchProgress(models.Model):
    """Tracks user playback position for 'Continue Watching'."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    last_position_seconds = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} - {self.video.title} ({self.last_position_seconds}s)"