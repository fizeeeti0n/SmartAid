from django.db import models
from django.conf import settings
from django.utils import timezone


class PlannerTask(models.Model):
    """
    Model representing a single task in the planner.
    """

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    # Links the task to the user who created it
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='planner_tasks',
        help_text="The user this task belongs to."
    )

    title = models.CharField(max_length=255, help_text="A brief title for the task.")
    description = models.TextField(blank=True, help_text="Detailed description of the task.")

    due_date = models.DateTimeField(null=True, blank=True, help_text="When the task is due.")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        help_text="Priority level of the task."
    )

    is_completed = models.BooleanField(default=False, help_text="Indicates if the task is done.")

    # Fields for Celery reminders
    reminder_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time to send a reminder (e.g., 30 mins before due date)."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-priority', 'created_at']
        verbose_name = "Planner Task"
        verbose_name_plural = "Planner Tasks"

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title} by {self.user.username}"
