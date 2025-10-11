from django.db import models
from django.contrib.auth.models import User


# --- Core Group Models ---

class StudyGroup(models.Model):
    """Represents a study group."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    # Link to the user who created the group
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def member_count(self):
        # Count the number of members using the reverse relationship
        return self.members.count()


class GroupMembership(models.Model):
    """Links a User to a StudyGroup."""
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only join a group once
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


# --- Chat/Communication Model ---

class GroupMessage(models.Model):
    """Stores chat messages for a group."""
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(max_length=2000)  # Add a reasonable limit
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)  # Index for faster queries

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Group Message"
        verbose_name_plural = "Group Messages"
        indexes = [
            models.Index(fields=['group', 'timestamp']),  # Optimize message fetching
        ]

    def __str__(self):
        return f"Msg by {self.user.username} in {self.group.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
