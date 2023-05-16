from django.db import models
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import pytz
from datetime import timedelta
from users.models import CustomUser

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Task(models.Model):

    PRIORITY_CHOICES = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    )

    CATEGORY_CHOICES = (
        ('P', 'Physical'),
        ('M', 'Mental'),
        ('S', 'Spiritual'),
    )

    FREQUENCY_CHOICES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, null=True, blank=True)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    frequency = models.CharField(max_length=1, choices=FREQUENCY_CHOICES)
    completion_goal = models.PositiveIntegerField(null=True, blank=True)
    completion_count = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=False)
    last_reset_date = models.DateField(auto_now_add=True, null=True)

    def create_history(self):
        TaskHistory.objects.create(
            task=self,
            user=self.user,
            title=self.title,
            description=self.description,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            completion_goal=self.completion_goal,
            completion_count=self.completion_count,
            status=self.status
        )

    def calculate_next_reset_date(self):
        # Get the current date in the user's timezone
        user_tz = pytz.timezone(self.user.timezone) #convert to pytz.timezone object
        now = timezone.localtime(timezone.now(), user_tz).date()
        
        if self.frequency == 'D':
            # For daily tasks, the next reset date is simply the next day
            return self.last_reset_date + timedelta(days=1)
        elif self.frequency == 'W':
            # For weekly tasks, find the next Sunday from the last reset date
            days_until_sunday = (6 - self.last_reset_date.weekday()) % 7
            next_sunday = self.last_reset_date + timedelta(days=days_until_sunday)
            return next_sunday
        elif self.frequency == 'M':
            # For monthly tasks, the next reset date is the first day of the next month
            if now.month == 12:
                next_month = now.replace(year=now.year+1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month+1, day=1)
            return next_month

    def __str__(self):
        return self.title

class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=1, choices=Task.PRIORITY_CHOICES, null=True, blank=True)
    category = models.CharField(max_length=1, choices=Task.CATEGORY_CHOICES)
    frequency = models.CharField(max_length=1, choices=Task.FREQUENCY_CHOICES)
    completion_goal = models.PositiveIntegerField(null=True, blank=True)
    completion_count = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Passion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class PassionActivity(models.Model):
    passion = models.ForeignKey(Passion, on_delete=models.CASCADE)
    date = models.DateField()
    duration = models.DurationField()

    def __str__(self):
        return f'{self.passion.name} on {self.date}'