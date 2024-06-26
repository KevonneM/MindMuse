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
    # Event URLS
    path('daily-view', views.daily_view, name='daily_view'),
    path('daily-view/<int:year>/<int:month>/<int:day>/', views.daily_view, name='daily_view_specific'),
    path('weekly-calendar/', views.weekly_calendar, name='weekly_calendar'),
    path('weekly-calendar/<str:start_date>/', views.weekly_calendar, name='weekly_calendar_change_week'),
    path('monthly-calendar/', views.monthly_calendar, name='monthly_calendar'),
    path('monthly-calendar/<int:year>/<int:month>/', views.monthly_calendar, name='monthly_calendar_change_month'),
    path('create-event/', views.create_event, name='create_event'),
    path('manage-events/', views.manage_events, name='manage_events'),
    path('manage-events/<int:year>/', views.manage_events, name='manage_events_year'),
    path('events/<int:pk>/delete/', views.delete_event, name="delete_event"),
    path('events/<int:pk>/edit/', views.update_event, name="update_event"),
    path('get_event_status/', views.get_event_status, name='get_event_status'),
    # Task URLS
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:pk>/edit/', views.update_task, name='update_task'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),
    # Passion URLS
    path('passions/create/', views.passion_create, name='passion_create'),
    path('passions/<int:pk>/update/', views.passion_update, name='passion_update'),
    path('passions/<int:pk>/delete/', views.passion_delete, name='passion_delete'),
    path('passions/<int:passion_pk>/activity/create/', views.passion_activity_create, name='passion_activity_create'),
    path('passions/record_activity/', views.record_passion_activity, name='record_passion_activity'),
    path('passions/delete_activity/', views.delete_passion_activity, name='delete_passion_activity'),
    path('passions/update_passion_progress/<int:pk>/', views.update_passion_progress, name='update_passion_progress'),
    path('passions/category/add/', views.add_passion_category, name='add_passion_category'),
    # Quote URLS
    path('quotes/create/', views.quote_create, name='quote_create'),
    path('quotes/<int:pk>/star/', views.quote_star, name='quote_star'),
    path('quotes/get_starred/', views.get_starred, name='get_starred'),
    path('quotes/<int:pk>/delete/', views.quote_delete, name='quote_delete'),
    path('quotes/<int:pk>/edit/', views.quote_edit, name='quote_edit'),
    path('get_quotes_of_the_day/', views.get_quotes_of_the_day, name='get_quotes_of_the_day'),
    path('qotd_save/<int:quote_id>/', views.qotd_save, name='qotd_save'),
]