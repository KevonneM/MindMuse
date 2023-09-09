from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.urls import reverse

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # logs the user in after signup
            login(request, user)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': 'ok', 'redirect_url': reverse('second_brain:home')})
            return redirect('second_brain:home')
    else:
        form = CustomUserCreationForm()

    if 'HTTP_X_REQUESTED_WITH' in request.META and request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
        return render(request, 'registration/_signup.html', {'form': form})
    else:
        return render(request, 'registration/signup.html', {'form': form})

def custom_login_view(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'ok', 'redirect_url': reverse('second_brain:home')})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        else:
            return redirect('second_brain:home')
    else:
        form = AuthenticationForm()
        # If it's an AJAX request, render only the login form, otherwise render the whole page.
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'registration/_login.html', {'form': form})
        else:
            return redirect('second_brain:home')

class CustomPasswordResetView(PasswordResetView):

    ajax_template_name = 'registration/_forgot_password.html'

    def get_template_names(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return [self.ajax_template_name]
        return super().get_template_names()
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 302:
            return JsonResponse({"success": "ok"})
        else:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                form_content = render_to_string(self.ajax_template_name, self.get_context_data())
                return JsonResponse({"success": "fail", "form_content": form_content}, status=400)
            return JsonResponse({"success": "fail"}, status=400)