from datetime import date
from django.utils import timezone
from celery import shared_task
from .models import Task, TaskHistory
import pytz

@shared_task
def refresh_tasks():
    for task in Task.objects.all():
        # Get the current date in the user's timezone
        user_tz = pytz.timezone(task.user.timezone)  # convert to pytz.timezone object
        now = timezone.localtime(timezone.now(), user_tz).date()

        next_reset_date = task.calculate_next_reset_date()
        print(f"This is a {task.frequency} task")
        print(f"Task {task.id}: next reset date = {next_reset_date}, now = {now}")

        # If the task's next reset date is today or in the past
        if task.calculate_next_reset_date() <= now:
            print(f"Resetting task {task.id}")
            # Create a new TaskHistory instance
            task.create_history()

            # Reset the task
            task.completion_count = 0
            task.status = False
            task.last_reset_date = now
            task.save()
        else:
            print(f"Not resetting task {task.id}")