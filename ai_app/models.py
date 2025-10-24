from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class AIInteractionLog(models.Model):
    """
    Logs every interaction with the Gemini API for auditing and analysis.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user who made the query."
    )
    prompt = models.TextField(help_text="The input query sent to the AI.")
    response = models.TextField(help_text="The AI's generated response.")
    is_successful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI Interaction Log"

    def __str__(self):
        return f"Log for {self.user.username if self.user else 'Anon'} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
class MoodLog(models.Model):
    """Stores a user's logged mood and the corresponding AI suggestion."""
    mood = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    ai_suggestion = models.TextField(blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order by newest entry first
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.mood} at {self.logged_at.strftime('%Y-%m-%d %H:%M')}"