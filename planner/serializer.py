from rest_framework import serializers
from .models import PlannerTask


class PlannerTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the PlannerTask model, used for converting Task objects
    to JSON and handling CRUD operations.
    """
    # Read-only field to display the user's ID
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    # Read-only field for human-readable priority
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = PlannerTask
        # Fields to expose in the API
        fields = [
            'id',
            'user',
            'title',
            'description',
            'due_date',
            'priority',
            'priority_display',
            'is_completed',
            'reminder_time',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        """
        Automatically sets the user to the currently authenticated user during creation.
        """
        # Ensure the user is set from the request context if not explicitly provided
        if 'user' not in validated_data and self.context['request'].user.is_authenticated:
            validated_data['user'] = self.context['request'].user

        return super().create(validated_data)
