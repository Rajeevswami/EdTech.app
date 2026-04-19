from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.section.course.title', read_only=True)
    
    class Meta:
        model = Video
        fields = ['id', 'lesson', 'lesson_title', 'course_title', 's3_url', 'file_size', 'duration', 'is_processed', 'created_at']
        read_only_fields = ['id', 's3_url', 'created_at']
