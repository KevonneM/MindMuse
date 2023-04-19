from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    path('insights/', views.insights, name='insights'),
]