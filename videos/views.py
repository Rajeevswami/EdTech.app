from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import logging

from .models import Video
from .serializers import VideoSerializer
from .s3_manager import S3VideoManager
from courses.models import Lesson

logger = logging.getLogger(__name__)

class VideoUploadViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        # Instructors see their own videos, students see enrolled course videos
        if self.request.user.profile.role == 'instructor':
            return Video.objects.filter(lesson__section__course__instructor=self.request.user)
        else:
            return Video.objects.filter(
                lesson__section__course__enrollments__student=self.request.user
            )
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload video to S3"""
        try:
            video_file = request.FILES.get('video')
            lesson_id = request.data.get('lesson_id')
            
            if not video_file or not lesson_id:
                return Response(
                    {'error': 'Video file and lesson_id required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get lesson
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                return Response(
                    {'error': 'Lesson not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check instructor permission
            if lesson.section.course.instructor != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check file size (500MB limit)
            if video_file.size > 500 * 1024 * 1024:
                return Response(
                    {'error': 'File size exceeds 500MB limit'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Upload to S3
            s3_manager = S3VideoManager()
            upload_result = s3_manager.upload_video(
                video_file,
                lesson_id,
                lesson.section.course.id
            )
            
            # Create or update video record
            video, created = Video.objects.get_or_create(
                lesson=lesson,
                defaults={
                    's3_key': upload_result['key'],
                    's3_url': upload_result['url'],
                    'file_size': upload_result['size'],
                    'is_processed': True
                }
            )
            
            if not created:
                video.s3_key = upload_result['key']
                video.s3_url = upload_result['url']
                video.file_size = upload_result['size']
                video.is_processed = True
                video.save()
            
            logger.info(f"Video uploaded: {video.id} by user {request.user.id}")
            
            serializer = self.get_serializer(video)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Video upload error: {str(e)}")
            return Response(
                {'error': 'Upload failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'])
    def delete_video(self, request, pk=None):
        """Delete video from S3 and database"""
        try:
            video = self.get_object()
            
            # Check permission
            if video.lesson.section.course.instructor != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete from S3
            s3_manager = S3VideoManager()
            s3_manager.delete_video(video.s3_key)
            
            # Delete from database
            video.delete()
            
            logger.info(f"Video deleted: {pk} by user {request.user.id}")
            
            return Response(
                {'success': True, 'message': 'Video deleted'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Exception as e:
            logger.error(f"Video deletion error: {str(e)}")
            return Response(
                {'error': 'Deletion failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
