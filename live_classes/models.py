from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
import uuid


class LiveClass(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('ended', 'Ended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_classes')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_classes')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', db_index=True)
    room_id = models.CharField(max_length=100, unique=True)
    max_participants = models.IntegerField(default=500)
    recording_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']
        indexes = [
            models.Index(fields=['course', '-scheduled_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} — {self.get_status_display()}"


class LiveClassParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attended_classes')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('live_class', 'student')
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.student.username} → {self.live_class.title}"


class LiveClassChat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['live_class', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.message[:60]}"
