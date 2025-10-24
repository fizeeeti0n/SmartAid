# ai_app/urls.py

from django.urls import path
from . import views

# Add this line to define the application namespace
app_name = 'ai_app'

urlpatterns = [
    # AI Assistant Chat Endpoint (Matches the frontend's expected URL)
    path('ai/plan/', views.AIChatView.as_view(), name='ai_chat'),

    # Mood Tracker Endpoint (Matches the frontend's expected URL)
    path('mood/save/', views.MoodLogView.as_view(), name='mood_log_save'),

    # Study Tools Endpoint for PDF processing
    path('study-tools/', views.StudyToolsView.as_view(), name='study_tools'),
]# ai_app/urls.py

from django.urls import path
from . import views

# Add this line to define the application namespace
app_name = 'ai_app'

urlpatterns = [
    # AI Assistant Chat Endpoint (Matches the frontend's expected URL)
    path('ai/plan/', views.AIChatView.as_view(), name='ai_chat'),

    # Mood Tracker Endpoint (Matches the frontend's expected URL)
    path('mood/save/', views.MoodLogView.as_view(), name='mood_log_save'),

    # Study Tools Endpoint for PDF processing
    path('study-tools/', views.StudyToolsView.as_view(), name='study_tools'),

    path('mood/save/', views.MoodLogView.as_view(), name='mood_log_save'),
]