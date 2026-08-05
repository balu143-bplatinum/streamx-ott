from django.db import models
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
    
    # 1. Direct Video File Upload (Supports MP4, MKV, AVI, MOV, WEBM)
    video_file = models.FileField(
        upload_to='videos/',
        storage=VideoMediaCloudinaryStorage(),
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'avi', 'mov', 'webm'])],
        help_text="Upload video file (MP4, MKV, AVI, MOV, WEBM)"
    )
    
    # 2. External Video Link (YouTube, HLS/M3U8, Direct CDN URL)
    external_video_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Optional: Paste a direct MP4/HLS link or external stream URL if not uploading a file"
    )

    # Poster / Thumbnail Image
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
        """Returns uploaded Cloudinary video URL if present; falls back to external_video_url."""
        if self.video_file:
            return self.video_file.url
        elif self.external_video_url:
            return self.external_video_url
        return ""

    @property
    def get_thumbnail_url(self):
        """Returns uploaded thumbnail URL or fallback stock poster image."""
        if self.thumbnail:
            return self.thumbnail.url
        return "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=600"


class AdCue(models.Model):
    """Model to manage Mid-Roll and Pre-Roll Video Ads for movies."""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='ad_cues')
    title = models.CharField(max_length=100, default="Sponsor Ad")
    
    # Ad Video File or External Ad Video Link
    ad_video_file = models.FileField(
        upload_to='ads/',
        storage=VideoMediaCloudinaryStorage(),
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'webm'])],
        help_text="Upload ad video file"
    )
    external_ad_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="External URL for the ad video if not uploaded"
    )
    
    # Sponsor Click Link
    sponsor_link = models.URLField(max_length=1000, default="https://google.com")
    
    # Timestamp in seconds when the ad should trigger during video playback (0 = Pre-roll)
    time_in_seconds = models.PositiveIntegerField(
        default=0, 
        help_text="Trigger timestamp in seconds (e.g., 300 for 5 minutes mark)"
    )

    def __str__(self):
        return f"{self.title} @ {self.time_in_seconds}s for {self.video.title}"

    @property
    def get_ad_url(self):
        if self.ad_video_file:
            return self.ad_video_file.url
        elif self.external_ad_url:
            return self.external_ad_url
        return ""