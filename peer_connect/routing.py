from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Uses slugified group name (e.g., 'Calculus_II_Problem_Set')
    re_path(r'ws/chat/(?P<group_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
