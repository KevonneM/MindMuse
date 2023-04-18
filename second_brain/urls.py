from django.urls import path
from . import views

app_name = 'second_brain'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('set_timezone', views.set_timezone, name='set_timezone'),
    path('fetch_weather/', views.fetch_weather, name='fetch_weather'),
    path('fetch_weather/<str:city>/', views.fetch_weather, name='fetch_weather_city'),
    path('get_last_tracked_city/', views.get_last_tracked_city, name='get_last_tracked_city')
]