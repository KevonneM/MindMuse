from django.contrib import admin
from .models import CustomUser, Payment

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Payment)
