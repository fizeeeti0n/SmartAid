from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    # Set the related_name to 'userprofile'
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    profile_pic = models.ImageField(upload_to='profile_pic', null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class Task(models.Model):
    """Represents a single task for the user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return f"{self.title} ({'Completed' if self.is_completed else 'Pending'})"

    # --- Mood Tracker Model ---


class MoodEntry(models.Model):
    """Represents a single mood logging entry."""
    MOOD_CHOICES = [
        ('joy', 'Joyful 😊'),
        ('calm', 'Calm 😌'),
        ('neutral', 'Neutral 😐'),
        ('tired', 'Tired 😴'),
        ('stressed', 'Stressed 😥'),
        ('sad', 'Sad 😞'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES)
    notes = models.TextField(blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"Mood: {self.get_mood_display()} at {self.logged_at.strftime('%Y-%m-%d %H:%M')}"


class Resource(models.Model):
    RESOURCE_CHOICES = [
        ('PDF', 'Document/PDF'),
        ('FLASHCARD', 'Flashcard Deck'),
        ('VIDEO', 'Video Link'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_CHOICES)

    # This field is crucial for file uploads
    file = models.FileField(upload_to='resources/pdfs/', blank=True, null=True)

    # This field is for video links or flashcard deck links
    url = models.URLField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title