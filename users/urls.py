from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .views import signup, custom_login_view

app_name = 'users'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', custom_login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]