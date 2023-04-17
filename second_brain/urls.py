from django.urls import path
from . import views

app_name = 'second_brain'

urlpatterns = [
    path('', views.home, name='home'),
    path('set_timezone', views.set_timezone, name='set_timezone'),
]