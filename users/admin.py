from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, VerificationToken

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_email_verified', 'city', 'created_at')
    list_filter = ('role', 'is_email_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'city')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Info', {
            'fields': ('phone', 'bio', 'avatar', 'role')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'pincode')
        }),
        ('Verification', {
            'fields': ('is_email_verified', 'is_phone_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_type', 'is_used', 'created_at', 'expires_at')
    list_filter = ('token_type', 'is_used', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)
