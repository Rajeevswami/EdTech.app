from django.db import models
from django.contrib.auth.models import User
import uuid


class Notification(models.Model):
    TYPE_CHOICES = [
        ('payment_success', 'Payment Success'),
        ('course_enrolled', 'Course Enrolled'),
        ('live_class_reminder', 'Live Class Reminder'),
        ('live_class_started', 'Live Class Started'),
        ('course_completed', 'Course Completed'),
        ('new_lesson', 'New Lesson Added'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    data = models.JSONField(default=dict, blank=True)  # extra payload (course_id, etc.)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.recipient.username} — {self.title}"
