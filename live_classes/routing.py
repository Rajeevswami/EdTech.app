from django.urls import re_path
from .consumers import LiveClassConsumer

websocket_urlpatterns = [
    re_path(r'^ws/live-class/(?P<live_class_id>[0-9a-f-]+)/$', LiveClassConsumer.as_asgi()),
]
