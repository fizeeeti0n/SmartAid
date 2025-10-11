# pc/urls.py (assuming this is part of your 'pc' app)

from django.urls import path
from . import views

app_name = 'st'

urlpatterns = [
    # ... existing URLs (peer_connect, chat_room, etc.)

    # URL for the study tools page
    path('study-tools/', views.study_tools_view, name='study_tools'),

    # URL for the flashcard creation endpoint
    path('study-tools/create-flashcards/', views.create_flashcards, name='create_flashcards'),

    # ... other URLs
]