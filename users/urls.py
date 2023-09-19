from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .views import signup, custom_login_view, CustomPasswordResetView, lemon_squeezy_webhook, link_existing_payment
from django.urls import reverse_lazy

app_name = 'users'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', custom_login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # django password reset urls
    path('password_reset/', CustomPasswordResetView.as_view(
        email_template_name='registration/custom_password_reset_email.html',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('mindmuse_lemon_squeezy_webhook/', lemon_squeezy_webhook, name='lemon_squeezy_webhook'),
    path('link_existing_payment/', link_existing_payment, name='link_existing_payment'),
]