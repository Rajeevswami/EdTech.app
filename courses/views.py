from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Q, Avg
from django.utils import timezone
import logging

from .models import Course, Section, Lesson, Enrollment, Review
from .serializers import (
    CourseDetailSerializer, CourseListSerializer, SectionSerializer,
    LessonSerializer, EnrollmentSerializer, ReviewSerializer
)

logger = logging.getLogger(__name__)

class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'is_published']
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'rating', 'price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Course.objects.all()
        return Course.objects.filter(is_published=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """Enroll student in course"""
        course = self.get_object()
        
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'error': 'Already enrolled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if course.price > 0:
            return Response(
                {'error': 'This is a paid course. Complete payment first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course
        )
        
        course.total_students += 1
        course.save()
        
        logger.info(f"User {request.user.id} enrolled in course {course.id}")
        
        return Response({
            'success': True,
            'enrollment_id': str(enrollment.id)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        """Add review to course"""
        course = self.get_object()
        
        # Check if already reviewed
        if Review.objects.filter(course=course, student=request.user).exists():
            return Response(
                {'error': 'You already reviewed this course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course, student=request.user)
            
            # Update course rating
            reviews = Review.objects.filter(course=course)
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            course.rating = avg_rating
            course.total_rating = reviews.count()
            course.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        if course_id:
            return Section.objects.filter(course_id=course_id)
        return Section.objects.all()


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']
    
    def get_queryset(self):
        section_id = self.request.query_params.get('section')
        if section_id:
            return Lesson.objects.filter(section_id=section_id)
        return Lesson.objects.all()


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['enrolled_at']
    ordering = ['-enrolled_at']
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_progress(self, request, pk=None):
        """Update course progress"""
        enrollment = self.get_object()
        progress = request.data.get('progress', 0)
        
        if 0 <= progress <= 100:
            enrollment.progress = progress
            if progress == 100:
                enrollment.completed = True
                enrollment.completed_at = timezone.now()
            enrollment.save()
            return Response({'success': True, 'progress': enrollment.progress})
        
        return Response(
            {'error': 'Progress must be between 0 and 100'},
            status=status.HTTP_400_BAD_REQUEST
        )
