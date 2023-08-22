from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from datetime import datetime, timedelta, date
from calendar import month_name
from django.db.models.functions import TruncDay
from django.db.models import Count
from .models import Event, Task, TaskHistory, Passion, PassionActivity, PassionCategory, Quote, QuoteOfTheDay
from .forms import TaskForm, PassionForm, PassionActivityForm, QuoteForm
import json
import requests
import pytz
import hashlib # for string to color function

# Create your views here.

def home(request):
    user = request.user
    events = []
    user_quotes = []

    if user.is_authenticated:

        if user.timezone:
            user_timezone = pytz.timezone(user.timezone)
        else:
            user_timezone = pytz.timezone('UTC')
        
        now = timezone.now().astimezone(user_timezone)
        today = now.date()

        # Making Sunday the first day of the week
        week_start = today - timedelta(days=((today.weekday() + 1) % 7))
        week_end = week_start + timedelta(days=7)

        # Task info for hub display
        daily_tasks = Task.objects.filter(user=request.user, frequency='D')
        weekly_tasks = Task.objects.filter(user=request.user, frequency='W')
        monthly_tasks = Task.objects.filter(user=request.user, frequency='M')

        # Passion info for hub display
        passions = Passion.objects.filter(user=request.user)
        passion_details = []
        passion_count = len(passions)

        week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        dates = [(i, week_start + timedelta(days=i)) for i in range(7)]
        current_weekday = (today.weekday() + 1) % 7

        for passion in passions:
            # Keep track of if checkbox has a recorded activity for that day.
            activities_this_week = PassionActivity.objects.filter(
                passion=passion,
                date__range=(dates[0][1], dates[-1][1])
            ).values_list('date', flat=True)

            activities_this_week = [activity.isoformat() for activity in activities_this_week]

            activities_exist = [date[1].isoformat() for date in dates if date[1].isoformat() in activities_this_week]

            passion_details.append({
                'passion': passion,
                'dates': dates,
                'week_days': week_days,
                'week_days_range': zip(list(range(7)), week_days),
                'activities_exist': activities_exist
            })

        # Event information for hub
        events = Event.objects.filter(user=user, start_time__gte=week_start, start_time__lt=week_end).order_by('start_time')
        visible_events = []
        all_events_invisible = True
        for event in events:
            event_start_time = event.start_time.replace(tzinfo=pytz.UTC)
            event_end_time = event.end_time.replace(tzinfo=pytz.UTC)

            # calculate the visibility of the event based on its start and end times
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            is_visible = now >= day_start and now < event_end_time + timedelta(minutes=5)

            if is_visible:
                all_events_invisible = False
            
            # add the event to the list with its visibility status
            visible_events.append({
                'event': event,
                'is_visible': is_visible,
            })
        if all_events_invisible:
            visible_events = []

        # Quotes for hub
        user_quotes = Quote.objects.filter(user=request.user)

        account_creation_year = user.date_joined.year

        context = {
            'events': visible_events,
            'daily_tasks': daily_tasks,
            'weekly_tasks': weekly_tasks,
            'monthly_tasks': monthly_tasks,
            'url_name': 'second_brain:home',
            'passion_details': passion_details,
            'current_weekday': current_weekday,
            'passion_count': passion_count,
            'user_quotes': user_quotes,
            'account_creation_year': account_creation_year,
            'is_authenticated': user.is_authenticated,
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

def get_event_status(request):
    user = request.user
    visible_events = []

    if user.is_authenticated:
        if user.timezone:
            user_timezone = pytz.timezone(user.timezone)
        else:
            user_timezone = pytz.timezone('UTC')
        
        now = timezone.now().astimezone(user_timezone)
        today = now.date()

        # Making Sunday the first day of the week
        week_start = today - timedelta(days=((today.weekday() + 1) % 7))
        week_end = week_start + timedelta(days=7)

        events = Event.objects.filter(user=user, start_time__gte=week_start, start_time__lt=week_end).order_by('start_time')

        all_events_invisible = True
        for event in events:
            event_start_time = event.start_time.replace(tzinfo=pytz.UTC)
            event_end_time = event.end_time.replace(tzinfo=pytz.UTC)

            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            is_visible = now >= day_start and now < event_end_time + timedelta(minutes=5)

            if is_visible:
                all_events_invisible = False
            
            visible_events.append({
                'event': event,
                'is_visible': is_visible,
            })
        
        if all_events_invisible:
            visible_events = []

    return JsonResponse({'has_visible_events': not all_events_invisible})

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
        return render(request, 'events/_daily_view.html', context)
    else:
        return redirect('second_brain:home')

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
        return render(request, 'events/_weekly_calendar.html', context)
    else:
        return redirect('second_brain:home')

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
        return render(request, 'events/_monthly_calendar.html', context)
    else:
        return redirect('second_brain:home')

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

    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, "events/_create_event.html")

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
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        if 'HTTP_X_REQUESTED_WITH' in request.META and request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
            try:
                task.status = request.POST.get('status') == 'true' # Get status from form
                task.save()

                # Get the most recent TaskHistory instance for this task
                task_history = TaskHistory.objects.filter(task=task).latest('created_at')
                task_history.status = task.status
                task_history.save()

                return JsonResponse({"success": True})
            except (ValueError, TypeError) as e:
                return JsonResponse({"success": False, "errors": str(e)}, status=400)
        else:
            return redirect('second_brain:home')
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'tasks/_task_detail.html', {'task': task})
        else:
            return redirect('second_brain:home')

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            task.create_history()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True})
            else:
                return redirect('second_brain:home')
    else:
        form = TaskForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'tasks/_create_task_form.html', {'form': form})
    else:
        return redirect('second_brain:home')

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

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True})
            else:
                return redirect('second_brain:home')
    else:
        form = TaskForm(instance=task)
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'tasks/_update_task_form.html', {'form': form, 'task': task})
    else:
        return redirect('second_brain:home')

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        return redirect('second_brain:home')
    
    elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'tasks/_task_confirm_delete.html', {'task': task})

    else:
        return HttpResponseBadRequest("Invalid request")

# Code for Passions/hobby progression tracking
@login_required
def passion_create(request):
    if request.method == 'POST':
        form = PassionForm(request.POST)
        if form.is_valid():
            passion = form.save(commit=False)
            passion.user = request.user
            passion.save()
            return redirect('second_brain:home')
    else:
        form = PassionForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'passions/_passion_form.html', {'form':form})

@login_required
def passion_update(request, pk):
    passion = get_object_or_404(Passion, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PassionForm(request.POST, instance=passion)
        if form.is_valid():
            passion = form.save()
            return redirect('second_brain:home')
    else:
        form = PassionForm(instance=passion)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'passions/_passion_update_form.html', {'form':form, 'passion': passion})

@login_required
def passion_delete(request, pk):
    passion = get_object_or_404(Passion, pk=pk, user=request.user)
    
    if request.method == 'POST':
        passion.delete()
        return redirect('second_brain:home')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'passions/_passion_confirm_delete.html', {'passion': passion})

# form submission from webpage
@login_required
def passion_activity_create(request, passion_pk):
    passion = get_object_or_404(Passion, pk=passion_pk, user=request.user)
    user_joined_year = request.user.date_joined.year
    
    if request.method == 'POST':
        form = PassionActivityForm(request.POST)
        if form.is_valid():
            activity_date = form.cleaned_data['date']

            if activity_date.year < user_joined_year:
                return JsonResponse({'success': False, 'message': 'Cannot record activity for years before your account was created.'})

            if activity_date > date.today():
                return JsonResponse({'success': False, 'message': 'Cannot record activity for future dates.'})

            hour = int(form.cleaned_data.get("hour"))
            minute = int(form.cleaned_data.get("minute"))
            duration_value = timedelta(hours=hour, minutes=minute)
            
            passion_activity, created = PassionActivity.objects.update_or_create(
                passion=passion, 
                date=form.cleaned_data['date'],
                defaults={'duration': duration_value}
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('second_brain:home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = PassionActivityForm()

    context = {
        'form': form,
        'passion': passion
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'passions/_passion_activity_form.html', context)

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

    last_sunday = current_date - timedelta(days=(current_date.weekday() + 1) % 7)
    dates = [(i, last_sunday + timedelta(days=i)) for i in range(7)]

    activities_this_week = PassionActivity.objects.filter(
        passion=passion,
        date__range=(dates[0][1], dates[-1][1])
    ).values_list('date', flat=True)

    activities_this_week = [activity.isoformat() for activity in activities_this_week]
    activities_exist = [str(date[1]) in activities_this_week for date in dates]

    return JsonResponse({'activities_exist': activities_exist})

@require_POST
def add_passion_category(request):
    data = json.loads(request.body)
    category_name = data.get('name')
    new_category = None

    if category_name:
        new_category, created = PassionCategory.objects.get_or_create(name=category_name)

    if new_category:
        return JsonResponse({'status': 'ok', 'id': new_category.id, 'name': new_category.name})

    return JsonResponse({'status': 'error', 'error': 'Invalid data.'})
    
# Code for quotes
@login_required
def quote_create(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            new_quote = form.save(commit=False)
            new_quote.user = request.user
            new_quote.save()

            return redirect('second_brain:home')
    else:
        form = QuoteForm()
    
    context = {'form': form}

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'quotes/_quote_form.html', context)

    return redirect('second_brain:home')

@login_required
def quote_star(request, pk):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        quote = get_object_or_404(Quote, pk=pk, user=request.user)

        if quote.starred:
            quote.starred = False
        else:
            Quote.objects.filter(user=request.user, starred=True).update(starred=False)
            quote.starred = True

        quote.save()

        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Not an AJAX request'})

@login_required
def get_starred(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        all_quotes = list(Quote.objects.filter(user=request.user))
    
        try:
            quote = Quote.objects.get(user=request.user, starred=True)
            all_quotes.remove(quote)
            all_quotes.insert(0, quote)
            quotes_json = [{'quote': q.quote, 'author': q.author, 'id': q.id, 'starred': q.starred} for q in all_quotes]
            return JsonResponse({
                'status': 'quote found',
                'quotes': quotes_json
            })
        except Quote.DoesNotExist:
            quotes_json = [{'quote': q.quote, 'author': q.author, 'id': q.id, 'starred': q.starred} for q in all_quotes]
            return JsonResponse({'status': 'no starred quote', 'quotes': quotes_json})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Not an AJAX request'})

@login_required
def quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk, user=request.user)
    
    if request.method == 'POST':
        quote.delete()
        return redirect('second_brain:home')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'quotes/_quote_confirm_delete.html', {'quote': quote})

@login_required
def quote_edit(request, pk):
    quote = get_object_or_404(Quote, pk=pk, user=request.user)

    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            return redirect('second_brain:home')

    else:
        form = QuoteForm(instance=quote)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'quotes/_quote_edit_form.html', {'form': form, 'quote': quote})

@login_required
def get_quotes_of_the_day(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user = request.user
        user_tz = pytz.timezone(user.get_timezone())
        now_in_user_tz = timezone.now().astimezone(user_tz)
        quotes_of_the_day = QuoteOfTheDay.objects.filter(created_at__date=now_in_user_tz.date()).values('id','quote', 'author')
        
        return JsonResponse({'quotes': list(quotes_of_the_day)}, safe=False)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def qotd_save(request, quote_id):
    qotd_instance = get_object_or_404(QuoteOfTheDay, id=quote_id)

    if request.method == 'POST':
        existing_quote = Quote.objects.filter(user=request.user, author=qotd_instance.author, quote=qotd_instance.quote).first()

        if existing_quote:
            data = {
                'success': False,
                'message': f"Quote from '{qotd_instance.author}' is already saved."
            }
            return JsonResponse(data)

        new_quote = Quote.objects.create(
            user = request.user,
            author = qotd_instance.author,
            quote = qotd_instance.quote
        )

        data = {
            'success': True,
            'quoteId': new_quote.id,
            'message': f"Quote from '{new_quote.author}' has been saved.",
            'author': new_quote.author
        }
        return JsonResponse(data)

    else:
        return render(request, 'quotes/_qotd_save.html', {'quote': qotd_instance})