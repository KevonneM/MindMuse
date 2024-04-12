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
        # New user flag
        is_new_user = self._state.adding

        # Calculate age based on date of birth
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            self.age = age
        super().save(*args, **kwargs)

        # Check flag and create color selection instance for the new user
        if is_new_user:
            SecondBrainColorSelection.objects.create(user=self)

class SecondBrainColorSelection(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    background_color = models.CharField(max_length=7, default='#1C3B3B')
    navigation_bar_color = models.CharField(max_length=7, default='#173234')
    button_color = models.CharField(max_length=7, default='#0B485A')
    tab_color = models.CharField(max_length=7, default='#1D8260')
    dropdown_color = models.CharField(max_length=7, default='#000000')
    logo_and_greeting_color = models.CharField(max_length=7, default='#FFFFFF')
    card_header_color = models.CharField(max_length=7, default='#397574')
    card_interior_color = models.CharField(max_length=7, default='#1B5657')
    title_text = models.CharField(max_length=7, default='#FFFFFF')
    button_text = models.CharField(max_length=7, default='#FFFFFF')
    tab_text = models.CharField(max_length=7, default='#FFFFFF')
    dropdown_text = models.CharField(max_length=7, default='#D3D3D3')
    text_color = models.CharField(max_length=7, default='#D3D3D3')

    def reset_to_defaults(self):
        self.background_color = '#1C3B3B'
        self.navigation_bar_color = '#173234'
        self.button_color = '#0B485A'
        self.tab_color = '#1D8260'
        self.dropdown_color = '#000000'
        self.logo_and_greeting_color = '#FFFFFF'
        self.card_header_color = '#397574'
        self.card_interior_color = '#1B5657'
        self.title_text = '#FFFFFF'
        self.button_text = '#FFFFFF'
        self.tab_text = '#FFFFFF'
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