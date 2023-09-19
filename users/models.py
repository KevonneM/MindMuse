from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date

# Create your models here.

# User model inheriting from Django's Abstract User.
class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=False)
    age = models.IntegerField(null=True, blank=False)
    timezone = models.CharField(max_length=100, null=True, blank=True)
    last_tracked_city = models.CharField(max_length=100, null=True, blank=True)

    def set_timezone(self, timezone_name):
        self.timezone = timezone_name
        self.save()
    
    def get_timezone(self):
        return self.timezone or timezone.get_default_timezone_name()
    
    def save(self, *args, **kwargs):
        # Calculate age based on date of birth
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            self.age = age
        super().save(*args, **kwargs)

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    payment_status = models.BooleanField(default=False)
    payment_email = models.EmailField(max_length=255, null=True, blank=True)
    transaction_id = models.CharField(unique=True, max_length=100, null=True)