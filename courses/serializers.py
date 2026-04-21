from rest_framework import serializers
from .models import Course, Section, Lesson, Enrollment, Review

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url', 'duration_minutes', 'order', 'is_preview', 'created_at']
        read_only_fields = ['id', 'created_at']


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'title', 'description', 'order', 'lessons', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'rating', 'review_text', 'student_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail', 'price', 'level',
            'category', 'duration_hours', 'total_students', 'rating', 'total_rating',
            'instructor_name', 'sections', 'reviews', 'is_enrolled', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user, course=obj
            ).exists()
        return False


class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'thumbnail', 'price', 'level', 'category',
            'total_students', 'rating', 'instructor_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_thumbnail = serializers.ImageField(source='course.thumbnail', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'course_thumbnail', 'progress', 'completed', 'enrolled_at']
        read_only_fields = ['id', 'enrolled_at']
