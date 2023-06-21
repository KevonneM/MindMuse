import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_structure.settings')

app = Celery('project_structure')

app.autodiscover_tasks()

app.conf.broker_url = 'redis://localhost:6379/0'

app.conf.beat_schedule = {
    'refresh-tasks-every-minute': {
        'task': 'second_brain.tasks.refresh_tasks', 
        'schedule': crontab(),  # Execute every minute
    },
}

app.conf.beat_schedule = {
    'fetch-and-save-quotes-of-the-day': {
        'task': 'second_brain.fetch_and_save_quotes_of_the_day',
        'schedule': crontab(minute=0, hour=0),
    }
}