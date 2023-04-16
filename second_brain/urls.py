from django.urls import path
from . import views

app_name = 'second_brain'

urlpatterns = [
    path('', views.home, name='home'),
]