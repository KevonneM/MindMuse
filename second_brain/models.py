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
    completion_goal = models.PositiveIntegerField(null=True, blank=True)
    completion_count = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=False)

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