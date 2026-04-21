from django.contrib import admin
from .models import LiveClass, LiveClassParticipant, LiveClassChat


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'instructor', 'status', 'scheduled_at', 'created_at')
    list_filter = ('status', 'scheduled_at', 'course')
    search_fields = ('title', 'instructor__username', 'course__title')
    readonly_fields = ('room_id', 'created_at')
    fieldsets = (
        ('Class Info', {'fields': ('course', 'instructor', 'title', 'description')}),
        ('Schedule', {'fields': ('scheduled_at', 'ended_at', 'status')}),
        ('Technical', {'fields': ('room_id', 'max_participants', 'recording_url')}),
        ('Meta', {'fields': ('created_at',)}),
    )


@admin.register(LiveClassParticipant)
class LiveClassParticipantAdmin(admin.ModelAdmin):
    list_display = ('student', 'live_class', 'joined_at', 'left_at')
    list_filter = ('live_class', 'joined_at')
    search_fields = ('student__username', 'live_class__title')
    readonly_fields = ('joined_at',)


@admin.register(LiveClassChat)
class LiveClassChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'live_class', 'message', 'created_at')
    list_filter = ('live_class', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
