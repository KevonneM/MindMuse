from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateField
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise ValidationError(_("Email field must not be empty"))

        return email.lower()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("That username is already taken.")
        return username

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email','first_name', 'last_name', 'date_of_birth', 'password1', 'password2')

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'date_of_birth']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise ValidationError(_("Email field must not be empty"))

        return email.lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user