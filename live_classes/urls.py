from django.urls import path
from .views import LiveClassViewSet

urlpatterns = [
    path('', LiveClassViewSet.as_view({'get': 'list', 'post': 'create'}), name='live-class-list'),
    path('<uuid:pk>/', LiveClassViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='live-class-detail'),
    path('<uuid:pk>/go-live/', LiveClassViewSet.as_view({'post': 'go_live'}), name='live-class-go-live'),
    path('<uuid:pk>/end/', LiveClassViewSet.as_view({'post': 'end_class'}), name='live-class-end'),
    path('<uuid:pk>/participants/', LiveClassViewSet.as_view({'get': 'participants'}), name='live-class-participants'),
    path('<uuid:pk>/chat/', LiveClassViewSet.as_view({'get': 'chat_history'}), name='live-class-chat'),
]
