from django.urls import path
from .views import NotificationViewSet

urlpatterns = [
    path('', NotificationViewSet.as_view({'get': 'list'}), name='notification-list'),
    path('unread/', NotificationViewSet.as_view({'get': 'unread'}), name='notification-unread'),
    path('mark-all-read/', NotificationViewSet.as_view({'patch': 'mark_all_read'}), name='notification-mark-all'),
    path('<uuid:pk>/read/', NotificationViewSet.as_view({'patch': 'mark_read'}), name='notification-read'),
]
