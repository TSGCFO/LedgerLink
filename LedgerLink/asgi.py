"""
ASGI config for LedgerLink project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# LedgerLink/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from ai_core import routing as ai_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ai_routing.websocket_urlpatterns
        )
    ),
})