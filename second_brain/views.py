from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta, date
from django.db.models.functions import TruncDay
from django.db.models import Count
from .models import Event
import requests
import pytz
import hashlib # for string to color function

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

def daily_view(request, year=None, month=None, day=None):
    user = request.user
    events = []

    if user.is_authenticated:
        user_timezone = pytz.timezone(user.timezone)

        if year and month and day:
            selected_date = datetime(year, month, day).date()
        else:
            now = timezone.now().astimezone(user_timezone)
            selected_date = now.date()

        start_of_day = user_timezone.localize(datetime(selected_date.year, selected_date.month, selected_date.day, 0, 0, 0))
        end_of_day = start_of_day + timezone.timedelta(days=1)
        events = Event.objects.filter(user=user, start_time__gte=start_of_day, start_time__lt=end_of_day).order_by('start_time')

    context = {
        'today': selected_date,
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

        # Color attribute for each event
        for event in events:
            event.color = string_to_color(event.title)

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

def monthly_calendar(request, year=None, month=None):
    if request.user.is_authenticated:
        user_timezone = pytz.timezone(request.user.timezone)
    else:
        user_timezone = pytz.UTC

    now = timezone.now().astimezone(user_timezone)

    if year is not None:
        current_year = int(year)
    else:
        current_year = now.year

    if month is not None:
        current_month = int(month)
    else:    
        current_month = now.month

    first_day_of_month = datetime(current_year, current_month, 1).date()
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    first_day_to_display = first_day_of_month - timedelta(days=(first_day_of_month.weekday() + 1) % 7)
    last_day_to_display = last_day_of_month + timedelta(days=(6 - last_day_of_month.weekday()))

    event_counts = Event.objects.filter(user=request.user, start_time__year=current_year, start_time__month=current_month).annotate(day=TruncDay('start_time', tzinfo=user_timezone)).values('day').annotate(count=Count('id')).values('day', 'count')

    event_by_day = {item['day'].date(): item['count'] for item in event_counts}

    calendar_data = []

    current_date = first_day_to_display
    while current_date <= last_day_to_display:
        week_data = []
        for _ in range(7):
            day_data = {
                'date': current_date,
                'event_count': event_by_day.get(current_date, 0) if current_date.month == current_month else None,
            }
            week_data.append(day_data)
            current_date += timedelta(days=1)
        calendar_data.append(week_data)

    prev_month = first_day_of_month - timedelta(days=1)
    next_month = last_day_of_month + timedelta(days=1)

    context = {
        'current_year': current_year,
        'current_month': current_month,
        'calendar_data': calendar_data,
        'prev_year': prev_month.year,
        'prev_month': prev_month.month,
        'next_year': next_month.year,
        'next_month': next_month.month,
    }

    return render(request, 'events/monthly_calendar.html', context)


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

def string_to_color(input_string):
    hash_object = hashlib.md5(input_string.encode())
    hexadecimal_of_hash = hash_object.hexdigest()
    return '#' + hexadecimal_of_hash[:6]