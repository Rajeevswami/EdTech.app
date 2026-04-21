from django.contrib import admin
from .models import Course, Section, Lesson, Enrollment, Review

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'level', 'price', 'total_students', 'rating', 'is_published', 'created_at')
    list_filter = ('level', 'category', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    readonly_fields = ('created_at', 'updated_at', 'total_students', 'rating', 'total_rating')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'instructor', 'thumbnail')
        }),
        ('Course Details', {
            'fields': ('level', 'category', 'price', 'duration_hours')
        }),
        ('Statistics', {
            'fields': ('total_students', 'rating', 'total_rating')
        }),
        ('Status', {
            'fields': ('is_published', 'created_at', 'updated_at')
        }),
    )

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'duration_minutes', 'is_preview', 'created_at')
    list_filter = ('section', 'is_preview', 'created_at')
    search_fields = ('title', 'section__title')
    ordering = ('section', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress', 'completed', 'enrolled_at')
    list_filter = ('course', 'completed', 'enrolled_at')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ('enrolled_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course', 'created_at')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ('created_at',)
