from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateField
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=200, help_text='Required')
    date_of_birth = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email','first_name', 'last_name', 'date_of_birth', 'password1', 'password2')