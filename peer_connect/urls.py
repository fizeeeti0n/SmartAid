from django.urls import path
from . import views

app_name = 'pc'

urlpatterns = [
    path('peer_connect/', views.peer_connect_view, name='peer_connect'),
    path('chat/<int:group_id>/', views.chat_room, name='chat_room'),

    # AJAX API routes - NO /api/ prefix (matches JavaScript URLs)
    path('send_message/<int:group_id>/', views.send_message, name='send_message'),
    path('fetch_messages/<int:group_id>/', views.fetch_messages, name='fetch_messages'),

    # Group actions
    path('join_group/<int:group_id>/', views.join_group, name='join_group'),
    path('leave_group/<int:group_id>/', views.leave_group, name='leave_group'),
    path('delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
]