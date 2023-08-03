from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    path('insights/', views.insights, name='insights'),
    path('yearly_event_data/<int:year>/', views.yearly_event_data, name='yearly_event_data'),
    path('yearly-task-completion-data/<int:year>/', views.yearly_task_completion_data, name='yearly_task_completion_data'),
]