# ai_core/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ai/features/$', consumers.AISystemConsumer.as_asgi()),
]