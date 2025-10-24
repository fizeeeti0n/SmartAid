

from rest_framework import serializers
from .models import MoodLog

class ChatRequestSerializer(serializers.Serializer):
    """Serializer for the AI Chat request."""
    message = serializers.CharField(max_length=2000)

class ChatResponseSerializer(serializers.Serializer):
    """Serializer for the AI Chat response."""
    response = serializers.CharField()

class MoodRequestSerializer(serializers.Serializer):
    """Serializer for the Mood Log request."""
    mood = serializers.CharField(max_length=50)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=1000)

class MoodResponseSerializer(serializers.Serializer):
    """Serializer for the Mood Log response."""
    mood = serializers.CharField()
    ai_suggestion = serializers.CharField()

class StudyToolResponseSerializer(serializers.Serializer):
    """Serializer for the Study Tools response."""
    summary = serializers.CharField()
    flashcards = serializers.JSONField() # List of {question, answer}
    title = serializers.CharField()


class MoodLogSerializer(serializers.Serializer):
    """Serializer for POST /api/mood/save/ (Request data)."""
    mood = serializers.CharField(max_length=50)
    notes = serializers.CharField(required=False, allow_blank=True)


class MoodLogFetchSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/mood/save/ (Response data)."""
    logged_at_display = serializers.SerializerMethodField()

    class Meta:
        model = MoodLog
        fields = ['mood', 'ai_suggestion', 'logged_at', 'logged_at_display']

    def get_logged_at_display(self, obj):
        # A simple method to make the date user-friendly (e.g., "5 minutes ago")
        from django.utils import timesince
        return f"{timesince.timesince(obj.logged_at)} ago"