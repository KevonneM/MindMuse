from django.db import models
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
    completion_goal = models.PositiveIntegerField(null=True, blank=True, help_text="Number of times the task should be completed in a week/month for weekly/monthly tasks")
    completion_count = models.PositiveIntegerField(default=0, help_text="Number of times the task has been completed")
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.title