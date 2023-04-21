from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from .models import Event
import requests
import pytz

# Create your views here.

def home(request):
    context = {'url_name': 'second_brain:home'}
    return render(request, 'home.html', context)

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

def fetch_weather(request, city=None):
    if request.user.is_authenticated:
        # Get the city from the user's profile or the 'city' parameter from search or ip geolocation api
        user_city = city or request.user.last_tracked_city
        api_key = settings.OPENWEATHERMAP_API_KEY

        # Fetch weather data from OpenWeatherMap API
        url = f'http://api.openweathermap.org/data/2.5/weather?q={user_city}&appid={api_key}&units=imperial'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Extract temperature and condition from the API response
            city_name = data['name']
            icon = data['weather'][0]['icon']
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            condition = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            context = {
                'city_name': city_name,
                'icon': icon,
                'temperature': temperature,
                'feels_like': feels_like,
                'condition': condition,
                'humidity': humidity,
                'wind_speed': wind_speed,
            }

            if city and city != request.user.last_tracked_city:
                request.user.last_tracked_city = city
                request.user.save()

            # Return the data as JSON
            return JsonResponse(context)
        else:
            return JsonResponse({'error': 'Failed to fetch weather data'}, status=500)
    else:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

def get_last_tracked_city(request):
    if request.user.is_authenticated:
        return JsonResponse({'last_tracked_city': request.user.last_tracked_city})
    else:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

def daily_view(request):
    user = request.user
    events = []

    if user.is_authenticated:
        user_timezone = pytz.timezone(user.timezone)
        now = timezone.now().astimezone(user_timezone)
        today = now.date()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timezone.timedelta(days=1)
        events = Event.objects.filter(user=user, start_time__gte=start_of_day, start_time__lt=end_of_day).order_by('start_time')

    context = {
        'today': today,
        'events': events,
    }

    return render(request, 'events/daily_view.html', context)

def weekly_calendar(request, start_date=None):
    user = request.user
    events = []

    if user.is_authenticated:
        user_timezone = pytz.timezone(user.timezone)
        if start_date:
            start_of_week = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=user_timezone)
        else:
            now = timezone.now().astimezone(user_timezone)
            start_of_week = now - timedelta(days=now.weekday() + 1 % 7)

        end_of_week = start_of_week + timedelta(days=7)
        events = Event.objects.filter(user=user, start_time__gte=start_of_week, start_time__lt=end_of_week).order_by('start_time')

        days = []
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            days.append({
                'weekday': i,
                'date': day_date
            })

        prev_week_start = start_of_week - timedelta(weeks=1)
        next_week_start = start_of_week + timedelta(weeks=1)

    context = {
        'days': days,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'prev_week_start': prev_week_start,
        'next_week_start': next_week_start,
        'events': events,
    }

    return render(request, 'events/weekly_calendar.html', context)

def create_event(request):
    if request.method == "POST":
        user = request.user
        title = request.POST.get("title")
        start_date = request.POST.get("start_date")
        start_time = request.POST.get("start_time")
        end_date = request.POST.get("end_date")
        end_time = request.POST.get("end_time")

        # Check if start_date, end_date, start_time, and end_time have values
        if start_date and start_time and end_date and end_time:
            # Convert start_date, end_date, start_time, and end_time to datetime objects for datepicker.
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_time = datetime.strptime(start_time, '%I:%M %p')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_time = datetime.strptime(end_time, '%I:%M %p')

            # Combines the date and time
            user_timezone = pytz.timezone(user.timezone)
            start_datetime = user_timezone.localize(start_date.replace(hour=start_time.hour, minute=start_time.minute))
            end_datetime = user_timezone.localize(end_date.replace(hour=end_time.hour, minute=end_time.minute))

            if is_event_overlapping(user, start_datetime, end_datetime):
                return JsonResponse({"status": "error", "message": "Event overlaps with an existing event."})
            else:
                # Create the event
                event = Event(user=user, title=title, start_time=start_datetime, end_time=end_datetime)
                event.save()

                return JsonResponse({"status": "success"})
        else:
            # Handle the case when any of the required values are missing
            return JsonResponse({"status": "error", "message": "Missing required values."})

    return render(request, "events/create_event.html")


def is_event_overlapping(user, start_time, end_time):
    overlapping_events = Event.objects.filter(
        user=user,
        start_time__lt=end_time,
        end_time__gt=start_time
    )

    same_start_end_time = Event.objects.filter(
        user=user,
        start_time=start_time,
        end_time=end_time
    )

    return overlapping_events.exists() or same_start_end_time.exists()