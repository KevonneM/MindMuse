from django.contrib import admin
from .models import Event, Task, TaskHistory, Passion, PassionActivity, Quote

# Register your models here.

admin.site.register(Event)
admin.site.register(Task)
admin.site.register(TaskHistory)
admin.site.register(Passion)
admin.site.register(PassionActivity)
admin.site.register(Quote)