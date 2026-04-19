from rest_framework import serializers
from .models import LiveClass, LiveClassParticipant, LiveClassChat


class LiveClassChatSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = LiveClassChat
        fields = ['id', 'username', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class LiveClassParticipantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = LiveClassParticipant
        fields = ['id', 'username', 'joined_at', 'left_at']
        read_only_fields = ['id', 'joined_at']


class LiveClassSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = LiveClass
        fields = [
            'id', 'course', 'course_title', 'instructor_name',
            'title', 'description', 'scheduled_at', 'ended_at',
            'status', 'room_id', 'max_participants', 'recording_url',
            'participant_count', 'created_at',
        ]
        read_only_fields = ['id', 'room_id', 'created_at']

    def get_participant_count(self, obj):
        return obj.participants.filter(left_at=None).count()


class LiveClassDetailSerializer(LiveClassSerializer):
    recent_chat = LiveClassChatSerializer(
        source='chat_messages', many=True, read_only=True
    )

    class Meta(LiveClassSerializer.Meta):
        fields = LiveClassSerializer.Meta.fields + ['recent_chat']
