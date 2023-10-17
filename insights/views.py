from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import pytz
from datetime import datetime, timedelta
import calendar
from second_brain.models import Event, TaskHistory, PassionActivity

# Create your views here.

def insights(request):
    user = request.user
    context = {'url_name': 'insights:insights'}

    if user.is_authenticated:
        user_timezone = pytz.timezone(user.timezone)
        now = timezone.now().astimezone(user_timezone)
        current_year = now.year
        account_creation_year = user.date_joined.year

        context = {
            'url_name': 'insights:insights',
            'current_year': current_year,
            'account_creation_year': account_creation_year,
        }

    return render(request, 'insights.html', context)

def yearly_event_data(request, year):
    user = request.user

    if user.is_authenticated:
        # Daily, Weekly, Monthly average calculations
        user_timezone = pytz.timezone(user.timezone)
        utc = pytz.timezone('UTC')

        start_of_year_local = user_timezone.localize(datetime(year, 1, 1, 0, 0, 0))
        end_of_year_local = start_of_year_local + relativedelta(years=1) - timedelta(seconds=1)

        start_of_year_utc = start_of_year_local.astimezone(utc)
        end_of_year_utc = end_of_year_local.astimezone(utc)
        # Fetch all relevent events from user
        events = list(Event.objects.filter(user=user, start_time__gte=start_of_year_utc, start_time__lte=end_of_year_utc))

        # Daily event data
        daily_event_data = []
        for day in range((end_of_year_local - start_of_year_local).days + 1):
            local_day_start = start_of_year_local + timedelta(days=day)
            local_day_end = local_day_start + timedelta(days=1, seconds=-1)
            daily_events = sum(e.start_time >= local_day_start.astimezone(utc) and e.start_time <= local_day_end.astimezone(utc) for e in events)
            daily_event_data.append({"date": local_day_start.strftime("%Y-%m-%d"), "events": daily_events})

        # Weekly event data
        weekly_bins = get_weekly_bins(start_of_year_local, end_of_year_local)
        weekly_event_data = []
        for week_start, week_end in weekly_bins:
            weekly_events = sum(e.start_time >= week_start.astimezone(utc) and e.start_time <= week_end.astimezone(utc) for e in events)
            weekly_event_data.append({
                "events": weekly_events,
                "start_date": week_start.date(),
                "end_date": week_end.date()
            })
        
        # Monthly event data
        monthly_event_data = []
        for month in range(1, 13):
            start_of_month_local = user_timezone.localize(datetime(year, month, 1, 0, 0, 0))
            if month == 12:
                end_of_month_local = end_of_year_local
            else:
                end_of_month_local = start_of_month_local + relativedelta(months=1) - timedelta(seconds=1)
            month_name = start_of_month_local.strftime("%B")
            monthly_events = sum(e.start_time >= start_of_month_local.astimezone(utc) and e.start_time < end_of_month_local.astimezone(utc) for e in events)
            monthly_event_data.append({"month": month_name, "events": monthly_events})

        # Calculating averages
        total_events = len(events)
        daily_average = total_events / len(daily_event_data) if daily_event_data else 0
        weekly_average = total_events / len(weekly_bins) if weekly_bins else 0
        monthly_average = total_events / len(monthly_event_data) if monthly_event_data else 0
        
        data = {
            'total_events': total_events,
            'daily_average': daily_average,
            'weekly_average': weekly_average,
            'monthly_average': monthly_average,
            'daily_event_data': daily_event_data,
            'weekly_event_data': weekly_event_data,
            'monthly_event_data': monthly_event_data
        }

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)

def get_weekly_bins(start_of_year_local, end_of_year_local):
    weekly_bins = []

    current_week_start = start_of_year_local
    current_week_end = start_of_year_local + timedelta(days=(5 - start_of_year_local.weekday()) % 7)
    current_week_end = current_week_end.replace(hour=23, minute=59, second=59)  
    
    while current_week_start < end_of_year_local:
        weekly_bins.append((current_week_start, current_week_end))
        
        current_week_start = current_week_end + timedelta(seconds=1)
        current_week_end = (current_week_start + timedelta(days=6)).replace(hour=23, minute=59, second=59)
        
        if current_week_end > end_of_year_local:
            current_week_end = end_of_year_local
            
    return weekly_bins

def yearly_task_completion_data(request, year):
    user = request.user

    if user.is_authenticated:
        user_timezone = pytz.timezone(user.timezone)
        utc = pytz.timezone('UTC')
        current_date_local = timezone.now().astimezone(user_timezone).date()

        start_of_year_local =user_timezone.localize(datetime(year, 1, 1, 0, 0))
        end_of_year_local = start_of_year_local + relativedelta(years=1) - timedelta(seconds=1)


        if year == timezone.now().year:
            # uncomment if i want to have chart display only up until current date/time.
            #now_local = timezone.now().astimezone(user_timezone)
            #end_of_year_local = user_timezone.localize(datetime(now_local.year, now_local.month, now_local.day, 23, 59,59))
            # Helps to provide information for entire year regardless of it being the current year.
            end_of_year_local = start_of_year_local + relativedelta(years=1) - timedelta(seconds=1)

            start_of_year_utc = start_of_year_local.astimezone(utc)
            end_of_year_utc = end_of_year_local.astimezone(utc)
        else:
            start_of_year_utc = start_of_year_local.astimezone(utc)
            end_of_year_utc = end_of_year_local.astimezone(utc)

        # Fetch all relevant tasks from user
        task_histories = TaskHistory.objects.filter(user=user, created_at__gte=start_of_year_utc, created_at__lte=end_of_year_utc)

        daily_task_histories = task_histories.filter(frequency='D')
        weekly_task_histories = task_histories.filter(frequency='W')
        monthly_task_histories = task_histories.filter(frequency='M')

        # Compute daily task completion rates
        daily_task_data = []
        for day in range((end_of_year_local - start_of_year_local).days + 1):
            local_day_start = start_of_year_local + timedelta(days=day)
            local_day_end = local_day_start + timedelta(days=1, seconds=-1)
            
            daily_tasks = daily_task_histories.filter(created_at__gte=local_day_start.astimezone(utc), created_at__lte=local_day_end.astimezone(utc))

            daily_tasks_completed = daily_tasks.filter(status=True).count()
            total_daily_tasks = daily_tasks.count()
            completion_rate = daily_tasks_completed / total_daily_tasks * 100 if total_daily_tasks != 0 else 0

            daily_task_data.append({
                'date': local_day_start.strftime("%Y-%m-%d"),
                'completed': daily_tasks_completed,
                'incompleted': total_daily_tasks - daily_tasks_completed,
                'total_tasks': total_daily_tasks,
                'completion_rate': completion_rate,
                'ratio': f"{daily_tasks_completed}/{total_daily_tasks}", 
            })

        # Compute weekly task completion rates
        weekly_bins = get_weekly_bins(start_of_year_local, end_of_year_local)
        weekly_task_data = []
        for week_start, week_end in weekly_bins:

            weekly_tasks = weekly_task_histories.filter(created_at__gte=week_start.astimezone(utc), created_at__lte=week_end.astimezone(utc))

            weekly_tasks_completed = weekly_tasks.filter(status=True).count()
            total_weekly_tasks = weekly_tasks.count()
            completion_rate = weekly_tasks_completed / total_weekly_tasks * 100 if total_weekly_tasks != 0 else 0

            weekly_task_data.append({
                'date': f"{week_start.date()} - {week_end.date()}",
                'completion_rate': completion_rate,
                'ratio': f"{weekly_tasks_completed}/{total_weekly_tasks}",
                'total_tasks': total_weekly_tasks,
                'completed': weekly_tasks_completed,
                'incompleted': total_weekly_tasks - weekly_tasks_completed,
            })

        # Compute monthly task completion rates
        monthly_task_data = []
        for month in range(1, 13):
            month_start_local = user_timezone.localize(datetime(year, month, 1, 0, 0, 0))

            if month == 12:
                month_end_local = end_of_year_local
            else:
                month_end_local = (month_start_local + relativedelta(months=1)) - timedelta(seconds=1)

            monthly_tasks = monthly_task_histories.filter(
                created_at__gte=month_start_local.astimezone(utc), 
                created_at__lte=month_end_local.astimezone(utc)
            )

            monthly_tasks_completed = monthly_tasks.filter(status=True).count()
            total_monthly_tasks = monthly_tasks.count()
            completion_rate = monthly_tasks_completed / total_monthly_tasks * 100 if total_monthly_tasks != 0 else 0

            monthly_task_data.append({
                'month': month_start_local.strftime("%B"),
                'completion_rate': completion_rate,
                'ratio': f"{monthly_tasks_completed}/{total_monthly_tasks}",
                'total_tasks': total_monthly_tasks,
                'completed': monthly_tasks_completed,
                'incompleted': total_monthly_tasks - monthly_tasks_completed
            })

        data = {
            'current_date': current_date_local.strftime('%Y-%m-%d'),
            'daily_task_data': daily_task_data,
            'weekly_task_data': weekly_task_data,
            'monthly_task_data': monthly_task_data
        }

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)

def yearly_passion_progress_data(request, year):
    user = request.user

    if user.is_authenticated:
        user_timezone = pytz.timezone(user.timezone)
        utc = pytz.timezone('UTC')

        start_of_year_utc = datetime(year, 1, 1, 0, 0, 0, tzinfo=utc)

        if year == timezone.now().year:
            now_utc = timezone.now().astimezone(utc)
            end_of_year_utc = utc.localize(datetime(now_utc.year, now_utc.month, now_utc.day, 23, 59,59))
        else:
            end_of_year_utc = start_of_year_utc + relativedelta(years=1) - timedelta(seconds=1)

        passion_activities = PassionActivity.objects.filter(passion__user=user, date__gte=start_of_year_utc.date(), date__lte=end_of_year_utc.date())
        weekly_passion_data = []

        # Compute weekly passion activity data
        current_week_start = start_of_year_utc
        current_week_end = start_of_year_utc + timedelta(days=(5 - start_of_year_utc.weekday()) % 7)
        current_week_end = current_week_end.replace(hour=23, minute=59, second=59)  # Set time to the end of Saturday
        while current_week_start < end_of_year_utc:

            week_data = {
                'date_range': f"{current_week_start.date()} - {current_week_end.date()}",
                'passions': {},
                'categories': {}
            }

            activities_for_week = passion_activities.filter(date__gte=current_week_start.date(), date__lte=current_week_end.date())
            
            for activity in activities_for_week:
                passion_name = activity.passion.name
                category_name = activity.passion.category.name if activity.passion.category else 'Uncategorized'
                passion_color = activity.passion.color

                if passion_name not in week_data['passions']:
                    week_data['passions'][passion_name] = {
                        'duration': timedelta(),
                        'color': passion_color,
                        'category': category_name
                    }

                if category_name not in week_data['categories']:
                    week_data['categories'][category_name] = timedelta()

                week_data['passions'][passion_name]['duration'] += activity.duration
                week_data['categories'][category_name] += activity.duration

            weekly_passion_data.append(week_data)

            # Move to the next Sunday
            current_week_start = current_week_end + timedelta(days=1)
            # Move to the following Saturday
            current_week_end = (current_week_start + timedelta(days=6)).replace(hour=23, minute=59, second=59)
            # Ensure the last week ends on Dec 31st
            if current_week_end > end_of_year_utc:
                current_week_end = end_of_year_utc

        data = {
            'weekly_passion_data': weekly_passion_data
        }

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)