from django.test import TestCase
from unittest.mock import patch
from django.utils import timezone
import datetime
import pytz
from second_brain.models import Task, CustomUser, TaskHistory

class TaskTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.user.timezone = 'UTC'
        self.user.save()

        self.daily_task = Task.objects.create(
            user=self.user,
            title='Daily task',
            frequency='D',
            last_reset_date=timezone.now().date() - timezone.timedelta(days=1)
        )
        # Determine the most recent past Sunday
        days_since_sunday = (timezone.now().date().weekday() - 6) % 7
        last_sunday = timezone.now().date() - timezone.timedelta(days=days_since_sunday)
        self.weekly_task = Task.objects.create(
            user=self.user,
            title='Weekly task',
            frequency='W',
            last_reset_date=last_sunday
        )
        self.monthly_task = Task.objects.create(
            user=self.user,
            title='Monthly task',
            frequency='M',
            last_reset_date=timezone.now().date().replace(day=1) - timezone.timedelta(days=1)
        )

    @patch('django.utils.timezone.now')
    def test_refresh_tasks(self, mock_now):
        mock_date = datetime.datetime(2023, 5, 14, tzinfo=timezone.utc)
        mock_now.return_value = mock_date

        from second_brain.tasks import refresh_tasks
        refresh_tasks()

        self.assertTrue(TaskHistory.objects.filter(task=self.daily_task).exists())
        self.assertTrue(TaskHistory.objects.filter(task=self.weekly_task).exists())
        self.assertFalse(TaskHistory.objects.filter(task=self.monthly_task).exists())

        self.daily_task.refresh_from_db()
        self.weekly_task.refresh_from_db()
        self.monthly_task.refresh_from_db()

        self.assertEqual(self.daily_task.completion_count, 0)
        self.assertEqual(self.weekly_task.completion_count, 0)
        self.assertEqual(self.monthly_task.completion_count, 0)

        self.assertEqual(self.daily_task.status, False)
        self.assertEqual(self.weekly_task.status, False)
        self.assertEqual(self.monthly_task.status, False)

        self.assertEqual(self.daily_task.last_reset_date, mock_date.date())
        self.assertEqual(self.weekly_task.last_reset_date, mock_date.date())
        self.assertEqual(self.monthly_task.last_reset_date, mock_date.date() - datetime.timedelta(days=1))
