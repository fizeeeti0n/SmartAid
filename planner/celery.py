from celery import shared_task
from django.core.mail import send_mail
from .models import PlannerTask


# NOTE: This file assumes Celery is configured and running in your Django environment.

@shared_task
def send_reminder_email(task_id):
    """
    Celery task to find a task by ID and send a reminder email to the user.
    This task would typically be scheduled when a task is created or updated
    with a valid `reminder_time`.
    """
    try:
        task = PlannerTask.objects.get(pk=task_id)
    except PlannerTask.DoesNotExist:
        # Task was likely deleted before the reminder fired, just exit gracefully.
        return

    # Prevent sending reminders for completed tasks (optional check)
    if task.is_completed:
        return

    subject = f"🔔 REMINDER: Task Due Soon - {task.title}"
    message = (
        f"Hi {task.user.username},\n\n"
        f"This is a reminder for your planner task:\n"
        f"Title: {task.title}\n"
        f"Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}\n"
        f"Description: {task.description or 'No description provided.'}\n\n"
        f"Please take action soon!"
    )

    # The recipient email address should be associated with the Django User model
    recipient_email = task.user.email

    if recipient_email:
        # In a real application, you would ensure Django's email backend is set up
        print(f"Sending reminder for Task ID {task_id} to {recipient_email}")

        # Example of sending email (requires email configuration in settings.py)
        # send_mail(
        #     subject,
        #     message,
        #     'no-reply@yourdomain.com', # Sender email address
        #     [recipient_email],
        #     fail_silently=False,
        # )
    else:
        print(f"Skipping reminder for Task ID {task_id}: User {task.user.username} has no email address.")
