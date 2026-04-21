from django.db import models
from courses.models import Lesson
import uuid

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='video')
    s3_key = models.CharField(max_length=500)
    s3_url = models.URLField()
    file_size = models.BigIntegerField()  # in bytes
    duration = models.IntegerField(default=0)  # in seconds
    upload_progress = models.IntegerField(default=0)  # 0-100%
    is_processed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lesson']),
        ]
    
    def __str__(self):
        return f"Video - {self.lesson.title}"
