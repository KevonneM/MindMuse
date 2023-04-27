from django.urls import path
from . import views

app_name = 'second_brain'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('set_timezone', views.set_timezone, name='set_timezone'),
    path('fetch_weather/', views.fetch_weather, name='fetch_weather'),
    path('fetch_weather/<str:city>/', views.fetch_weather, name='fetch_weather_city'),
    path('get_last_tracked_city/', views.get_last_tracked_city, name='get_last_tracked_city'),
    path('incoming_events_this_week/', views.incoming_events_this_week, name='incoming_events_this_week'),
    path('daily-view', views.daily_view, name='daily_view'),
    path('daily-view/<int:year>/<int:month>/<int:day>/', views.daily_view, name='daily_view_specific'),
    path('weekly-calendar/', views.weekly_calendar, name='weekly_calendar'),
    path('weekly-calendar/<str:start_date>/', views.weekly_calendar, name='weekly_calendar_change_week'),
    path('monthly-calendar/', views.monthly_calendar, name='monthly_calendar'),
    path('monthly-calendar/<int:year>/<int:month>/', views.monthly_calendar, name='monthly_calendar_change_month'),
    path('create-event/', views.create_event, name='create_event')
]