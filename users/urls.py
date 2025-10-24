from django.urls import path
from . import views # Correctly imports views from planner/views.py

urlpatterns = [
    # General views
    path('', views.index, name='index'),  # This will be your site root (mysite.com/)
   # path('peer-connect/', views.peer_connect, name='peer_connect'),
    path('study-tools/', views.study_tools, name='study_tools'),
    path('resource-library/', views.resource_library, name='resource_library'),

    # Assuming your view function is named 'signup_view' in planner/views.py
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),  # <-- FIXED: Changed 'views.signup' to 'views.signup_view'
    path('logout/', views.logout, name='logout'),
    path('user_profile/', views.profile, name='user_profile'),
    path('library/', views.resource_library, name='resource_library'),

    # 2. URL for PDF/Document Upload (The one giving you the 404)
    path('upload-document', views.upload_document, name='upload_document'),

    # 3. URL for Flashcard Submission
    path('save-flashcard', views.save_flashcard, name='save_flashcard'),

    # 4. URL for Video Link Submission
    path('save-video', views.save_video, name='save_video'),
]