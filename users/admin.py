from django.contrib import admin
from .models import CustomUser, Payment, SecondBrainColorSelection

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Payment)
admin.site.register(SecondBrainColorSelection)
