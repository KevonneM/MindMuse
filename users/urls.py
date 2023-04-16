from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

app_name = 'users'

urlpatterns = [
    path('signup/', CreateView.as_view(
        template_name='registration/signup.html',
        form_class=UserCreationForm,
        success_url='/'
    ), name='signup'),
    path('login/', LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
]