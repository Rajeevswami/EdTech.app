from django.urls import path
from .views import register, login, logout, UserViewSet

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', UserViewSet.as_view({'get': 'me', 'put': 'update_profile', 'patch': 'update_profile'}), name='profile'),
    path('change-password/', UserViewSet.as_view({'post': 'change_password'}), name='change-password'),
]
