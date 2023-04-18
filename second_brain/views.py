from django.shortcuts import render
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.

def home(request):
    return render(request, 'home.html')

def profile(request):
    return render(request, 'profile.html')

@csrf_exempt
def set_timezone(request):
    if request.method == 'POST':
        timezone = request.POST.get('timezone')
        request.user.set_timezone(timezone)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})