from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Import ViewSets
from courses.views import CourseViewSet, SectionViewSet, LessonViewSet, EnrollmentViewSet
from payments.views import OrderViewSet, PaymentViewSet
from users.views import UserViewSet, UserProfileViewSet
from videos.views import VideoUploadViewSet
from live_classes.views import LiveClassViewSet, LiveClassChatViewSet

# Create router
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'videos', VideoUploadViewSet, basename='video')
router.register(r'live-classes', LiveClassViewSet, basename='live-class')
router.register(r'live-classes-chat', LiveClassChatViewSet, basename='live-class-chat')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/auth/', include('users.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/live/', include('live_classes.urls')),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
