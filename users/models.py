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

class SecondBrainColorSelection(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    background_color = models.CharField(max_length=7, default='#2D2350')
    navigation_bar_color = models.CharField(max_length=7, default='#452475')
    button_color = models.CharField(max_length=7, default='#7638C2')
    tab_color = models.CharField(max_length=7, default='#A78EEF')
    dropdown_color = models.CharField(max_length=7, default='#452475')
    logo_and_greeting_color = models.CharField(max_length=7, default='#FFFFFF')
    card_header_color = models.CharField(max_length=7, default='#673AB7')
    card_interior_color = models.CharField(max_length=7, default='#58349D')
    title_text = models.CharField(max_length=7, default='#D3D3D3')
    button_text = models.CharField(max_length=7, default='#FFFFFF')
    tab_text = models.CharField(max_length=7, default='#D3D3D3')
    dropdown_text = models.CharField(max_length=7, default='#D3D3D3')
    text_color = models.CharField(max_length=7, default='#D3D3D3')

    def reset_to_defaults(self):
        self.background_color = '#2D2350'
        self.navigation_bar_color = '#452475'
        self.button_color = '#7638C2'
        self.tab_color = '#A78EEF'
        self.dropdown_color = '#452475'
        self.logo_and_greeting_color = '#FFFFFF'
        self.card_header_color = '#673AB7'
        self.card_interior_color = '#58349D'
        self.title_text = '#D3D3D3'
        self.button_text = '#FFFFFF'
        self.tab_text = '#D3D3D3'
        self.dropdown_text = '#D3D3D3'
        self.text_color = '#D3D3D3'
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Color Selection"

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    payment_status = models.BooleanField(default=False)
    payment_email = models.EmailField(max_length=255, null=True, blank=True)
    # customer_id from lemon squeezy.
    transaction_id = models.CharField(unique=True, max_length=100, null=True)
    # subscription_id from lemon squeezy.
    subscription_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'Payment object under {self.payment_email}, for {self.user}'