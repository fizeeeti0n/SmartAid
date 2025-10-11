"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import peer_connect.routing # Import your app's routing

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django_asgi_app = get_asgi_application() # Get Django's ASGI application

# Define routing for HTTP and WebSocket
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            peer_connect.routing.websocket_urlpatterns
        )
    ),
})
