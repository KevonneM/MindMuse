from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateField
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=30, required=True, help_text='Required.',
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, required=True, help_text='Required.',
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        max_length=200, help_text='Required.',
        widget=forms.TextInput(attrs={'placeholder': 'Email'})
    )
    date_of_birth = DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date', 'placeholder': 'Date of Birth'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email','first_name', 'last_name', 'date_of_birth', 'password1', 'password2')