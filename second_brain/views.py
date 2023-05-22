from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta, date
from calendar import month_name
from django.db.models.functions import TruncDay
from django.db.models import Count
from .models import Event, Task, TaskHistory, Passion, PassionActivity
from .forms import TaskForm, PassionForm, PassionActivityForm
import json
import requests
import pytz
import hashlib # for string to color function

# Create your views here.

def home(request):
    user = request.user
    events = []

    if user.is_authenticated:
        user_timezone = pytz.timezone(user.timezone)
        now = timezone.now().astimezone(user_timezone)
        today = now.date()

        # Making Sunday the first day of the week
        week_start = today - timedelta(days=((today.weekday() + 1) % 7))
        week_end = week_start + timedelta(days=7)

        events = Event.objects.filter(user=user, start_time__gte=week_start, start_time__lt=week_end).order_by('start_time')

        # Task info for hub display
        daily_tasks = Task.objects.filter(user=request.user, frequency='D')
        weekly_tasks = Task.objects.filter(user=request.user, frequency='W')
        monthly_tasks = Task.objects.filter(user=request.user, frequency='M')

        context = {
            'events': events,
            'daily_tasks': daily_tasks,
            'weekly_tasks': weekly_tasks,
            'monthly_tasks': monthly_tasks,
            'url_name': 'second_brain:home'
        }
    else:
        context = {
            'url_name': 'second_brain:home'
        }
    return render(request, 'home.html', context)

@login_required
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

# Code for Events

@login_required
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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'modal_templates/_daily_view.html', context)
    else:
        return render(request, 'events/daily_view.html', context)

@login_required
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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'modal_templates/_weekly_calendar.html', context)
    else:
        return render(request, 'events/weekly_calendar.html', context)

@login_required
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

    current_month_name = month_name[current_month]

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
        'current_month_name': current_month_name,
        'calendar_data': calendar_data,
        'prev_year': prev_month.year,
        'prev_month': prev_month.month,
        'next_year': next_month.year,
        'next_month': next_month.month,
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'modal_templates/_monthly_calendar.html', context)
    else:
        return render(request, 'events/monthly_calendar.html', context)

@login_required
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

# Code for Tasks

def task_list(request):
    daily_tasks = Task.objects.filter(user=request.user, frequency='D')
    weekly_tasks = Task.objects.filter(user=request.user, frequency='W')
    monthly_tasks = Task.objects.filter(user=request.user, frequency='M')

    context = {
        'daily_tasks': daily_tasks,
        'weekly_tasks': weekly_tasks,
        'monthly_tasks': monthly_tasks,
    }

    return render(request, 'tasks/task_list.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        if 'HTTP_X_REQUESTED_WITH' in request.META and request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
            print("AJAX request detected")
            try:
                task.status = request.POST.get('status') == 'true' # Get status from form
                task.save()

                # Get the most recent TaskHistory instance for this task
                task_history = TaskHistory.objects.filter(task=task).latest('created_at')
        
                task_history.status = task.status
                task_history.save()

                return JsonResponse({'success': True})

            except (ValueError, TypeError) as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
        else:
            print("not ajax")

    context = {
        'task': task,
    }

    return render(request, 'tasks/task_detail.html', context)

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            task.create_history()
            return redirect('second_brain:home')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            # Get the most recent TaskHistory instance for this task
            task_history = TaskHistory.objects.filter(task=task).latest('created_at')
            
            task_history.title = task.title
            task_history.description = task.description
            task_history.priority = task.priority
            task_history.category = task.category
            task_history.frequency = task.frequency
            task_history.status = task.status
            task_history.save()

            return redirect('second_brain:home')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()

    return redirect('second_brain:task_list')

# Code for Passions/hobby progression tracking

@login_required
def passion_list(request):
    passions = Passion.objects.filter(user=request.user)

    context = {
        'passions': passions,
    }

    return render(request, 'passions/passion_list.html', context)

@login_required
def passion_detail(request, pk):
    passion = get_object_or_404(Passion, pk=pk, user=request.user)
    passion_activities = PassionActivity.objects.filter(passion=passion)

    user_timezone = request.user.timezone
    tz = pytz.timezone(user_timezone)

    current_date = timezone.now().astimezone(tz).date()
    current_weekday = (current_date.weekday() + 1) % 7

    last_sunday = current_date - timedelta(days=current_date.weekday() + 1)

    dates = [(i, last_sunday + timedelta(days=i)) for i in range(7)]
    week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # Keep track of if checkbox has a recorded activity for that day.
    activities_this_week = PassionActivity.objects.filter(
        passion=passion,
        date__range=(dates[0][1], dates[-1][1])
    ).values_list('date', flat=True)

    activities_this_week = [activity.isoformat() for activity in activities_this_week]

    activities_exist = [date[1].isoformat() for date in dates if date[1].isoformat() in activities_this_week]

    context = {
        'passion': passion,
        'passion_activities': passion_activities,
        'dates': dates,
        'current_date': current_date,
        'current_weekday': current_weekday,
        'week_days': week_days,
        'week_days_range': zip(list(range(7)), week_days),
        'activities_exist': activities_exist
    }

    return render(request, 'passions/passion_detail.html', context)

@login_required
def passion_create(request):
    if request.method == 'POST':
        form = PassionForm(request.POST)
        if form.is_valid():
            passion = form.save(commit=False)
            passion.user = request.user
            passion.save()
            return redirect('second_brain:passion_detail', pk=passion.pk)
    else:
        form = PassionForm()

    return render(request, 'passions/passion_form.html', {'form': form})

@login_required
def passion_update(request, pk):
    passion = get_object_or_404(Passion, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PassionForm(request.POST, instance=passion)
        if form.is_valid():
            passion = form.save()
            return redirect('second_brain:passion_detail', pk=passion.pk)
    else:
        form = PassionForm(instance=passion)

    return render(request, 'passions/passion_form.html', {'form': form})

@login_required
def passion_delete(request, pk):
    passion = get_object_or_404(Passion, pk=pk, user=request.user)
    
    if request.method == 'POST':
        passion.delete()
        return redirect('second_brain:passion_list')

    return render(request, 'passions/passion_confirm_delete.html', {'passion': passion})

# form submission from webpage
@login_required
def passion_activity_create(request, passion_pk):
    passion = get_object_or_404(Passion, pk=passion_pk, user=request.user)
    
    if request.method == 'POST':
        form = PassionActivityForm(request.POST)
        if form.is_valid():
            passion_activity = form.save(commit=False)
            passion_activity.passion = passion
            passion_activity.save()
            return redirect('second_brain:passion_detail', pk=passion.pk)
    else:
        form = PassionActivityForm()

    context = {
        'form': form,
        'passion': passion
        }

    return render(request, 'passions/passion_activity_form.html', context)

# Ajax update for passion activity tracking
@csrf_exempt
@login_required
def record_passion_activity(request):
    if request.method == 'POST':
        if 'HTTP_X_REQUESTED_WITH' in request.META and request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
            print("AJAX request detected")

            data = json.loads(request.body)
            passion_id = data.get('passion_id')
            date = data.get('date')
            hours = data.get('hours')
            minutes = data.get('minutes')

            passion = get_object_or_404(Passion, pk=passion_id, user=request.user)
            duration = timedelta(hours=int(hours), minutes=int(minutes))

            # Check if one exists, then update duration
            passion_activity, created = PassionActivity.objects.get_or_create(
                passion=passion,
                date=date,
                defaults={'duration': duration}
            )

            if not created:
                passion_activity.duration = duration
                passion_activity.save()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def delete_passion_activity(request):
    if request.method == 'POST':
        if 'HTTP_X_REQUESTED_WITH' in request.META and request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
            print("AJAX delete request detected")

            data = json.loads(request.body)
            passion_id = data.get('passion_id')
            date = data.get('date')

            passion = get_object_or_404(Passion, pk=passion_id, user=request.user)

            try:
                passion_activity = PassionActivity.objects.get(passion=passion, date=date)
                passion_activity.delete()
                return JsonResponse({'success': True})
            except PassionActivity.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'PassionActivity not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def update_passion_progress(request, pk):
    
    passion = get_object_or_404(Passion, pk=pk, user=request.user)
    tz = pytz.timezone(request.user.timezone)
    current_date = timezone.now().astimezone(tz).date()

    last_sunday = current_date - timedelta(days=current_date.weekday() + 1)
    dates = [(i, last_sunday + timedelta(days=i)) for i in range(7)]

    activities_this_week = PassionActivity.objects.filter(
        passion=passion,
        date__range=(dates[0][1], dates[-1][1])
    ).values_list('date', flat=True)

    activities_this_week = [activity.isoformat() for activity in activities_this_week]
    activities_exist = [str(date[1]) in activities_this_week for date in dates]

    return JsonResponse({'activities_exist': activities_exist})