"""
URL configuration for mysite project.
...
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Import settings
from django.conf.urls.static import static  # Import static

# You MUST NOT have 'from . import views' here. Instead, route to the app.



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('peer-connect/', include('peer_connect.urls')),
    path('study_tools/', include('study_tools.urls')),
    path('api/ai/', include('ai_app.urls', namespace='ai_app')),
]


# Add URL patterns for serving static AND media files in development
if settings.DEBUG:
    # This line serves your static files (like CSS, JS)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # 🌟 THIS LINE FIXES YOUR MEDIA FILE 404 ERROR 🌟
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)