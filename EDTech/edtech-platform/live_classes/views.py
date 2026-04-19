import uuid
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging

from .models import LiveClass, LiveClassParticipant, LiveClassChat
from .serializers import (
    LiveClassSerializer, LiveClassDetailSerializer,
    LiveClassChatSerializer, LiveClassParticipantSerializer,
)

logger = logging.getLogger(__name__)


class LiveClassViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['scheduled_at', 'status']
    ordering = ['-scheduled_at']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role == 'instructor':
            return LiveClass.objects.filter(instructor=user)
        # Students see live classes of their enrolled courses
        return LiveClass.objects.filter(
            course__enrollments__student=user
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LiveClassDetailSerializer
        return LiveClassSerializer

    def perform_create(self, serializer):
        # Auto-generate unique room_id
        serializer.save(
            instructor=self.request.user,
            room_id=str(uuid.uuid4()).replace('-', '')[:20],
        )

    @action(detail=True, methods=['post'])
    def go_live(self, request, pk=None):
        """Instructor starts the live class"""
        live_class = self.get_object()
        if live_class.instructor != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        live_class.status = 'live'
        live_class.save()
        logger.info(f"LiveClass {live_class.id} is now LIVE")
        return Response({'status': 'live', 'room_id': live_class.room_id})

    @action(detail=True, methods=['post'])
    def end_class(self, request, pk=None):
        """Instructor ends the live class"""
        live_class = self.get_object()
        if live_class.instructor != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        live_class.status = 'ended'
        live_class.ended_at = timezone.now()
        live_class.save()
        logger.info(f"LiveClass {live_class.id} ended")
        return Response({'status': 'ended'})

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get current participants"""
        live_class = self.get_object()
        qs = live_class.participants.filter(left_at=None)
        serializer = LiveClassParticipantSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def chat_history(self, request, pk=None):
        """Get last 100 chat messages"""
        live_class = self.get_object()
        messages = live_class.chat_messages.order_by('-created_at')[:100]
        serializer = LiveClassChatSerializer(reversed(list(messages)), many=True)
        return Response(serializer.data)


class LiveClassChatViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LiveClassChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        live_class_id = self.request.query_params.get('live_class')
        if live_class_id:
            return LiveClassChat.objects.filter(live_class_id=live_class_id)
        return LiveClassChat.objects.none()
