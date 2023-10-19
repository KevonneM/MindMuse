from datetime import date, timedelta
from django.utils import timezone
from celery import shared_task
from .models import Task, TaskHistory, QuoteOfTheDay
import pytz
import requests

@shared_task
def refresh_tasks():
    for task in Task.objects.all():
        # Get the current date in the user's timezone
        user_tz = pytz.timezone(task.user.timezone)  # convert to pytz.timezone object
        now = timezone.localtime(timezone.now(), user_tz)
        now_date = now.date()

        middle_of_day_local = now.replace(hour=12, minute=0, second=0)

        next_reset_date = task.calculate_next_reset_date()
        print(f"This is a {task.frequency} task")
        print(f"Task {task.id}: next reset date = {next_reset_date}, now = {now}")

        # If the task's next reset date is today or in the past
        # AND the task hasn't been reset today yet
        if ( next_reset_date == now_date and (task.last_reset_time is None or timezone.localtime(task.last_reset_time, user_tz).date() != now_date)):

            print(f"Resetting task {task.id}: next reset date = {next_reset_date}, now = {now}")

            # Reset the task
            task.status = False
            task.last_reset_date = middle_of_day_local.date()
            task.last_reset_time = middle_of_day_local
            task.save()
            task.create_history()
        else:
            print(f"Not resetting task {task.id}")

@shared_task
def fetch_and_save_quotes_of_the_day():
    """
    three_day_ago var enables users in different timezones that may be behind server timezone to always have quotes to view and accounts for the edge case where some user's local timezones
    could be almost a full day behind the server's timezone.
    """
    three_days_ago = timezone.now() - timedelta(days=3)
    QuoteOfTheDay.objects.filter(created_at__date__lt=three_days_ago).delete()

    try:
        response = requests.get('https://zenquotes.io/api/quotes/')
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request to fetch quote of the day failed: {e}")
        return

    data = response.json()

    if not data:
        print("No data received for quote of the day.")
        return

    for quote in data:
        quote_of_The_day = QuoteOfTheDay.objects.create(
            quote=quote['q'],
            author=quote['a'],
            created_at=timezone.now()
        )
        quote_of_The_day.save()
