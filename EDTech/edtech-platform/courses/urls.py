from django.urls import path
from .views import CourseViewSet

urlpatterns = [
    # Course list and detail
    path('', CourseViewSet.as_view({'get': 'list', 'post': 'create'}), name='course-list'),
    path('<uuid:pk>/', CourseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='course-detail'),
    
    # Course actions
    path('<uuid:pk>/enroll/', CourseViewSet.as_view({'post': 'enroll'}), name='course-enroll'),
    path('<uuid:pk>/review/', CourseViewSet.as_view({'post': 'add_review'}), name='course-review'),
]
