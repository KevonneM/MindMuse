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
        
        start_of_year_utc = datetime(year, 1, 1, 0, 0, 0, tzinfo=utc)

        end_of_year_utc = start_of_year_utc + relativedelta(years=1) - timedelta(seconds=1)

        total_events = Event.objects.filter(user=user, start_time__gte=start_of_year_utc, start_time__lt=end_of_year_utc).count()
        days_elapsed = (end_of_year_utc - start_of_year_utc).days + 1
        daily_average = total_events / days_elapsed if days_elapsed > 0 else 0

        start_of_month_utc = start_of_year_utc
        months_elapsed = (end_of_year_utc.month - start_of_year_utc.month) + (end_of_year_utc.day / calendar.monthrange(year, end_of_year_utc.month)[1])
        monthly_average = total_events / months_elapsed if months_elapsed > 0 else 0

        weekly_event_data = []
        daily_event_data = []
        monthly_event_data = []

        for day in range(days_elapsed):

            local_day_start = user_timezone.localize(datetime(year, 1, 1, 0, 0, 0)) + timedelta(days=day)
            local_day_end = local_day_start + timedelta(days=1, seconds=-1)

            day_start_utc = local_day_start.astimezone(utc)
            day_end_utc = local_day_end.astimezone(utc)

            daily_events = Event.objects.filter(user=user, start_time__gte=day_start_utc, start_time__lt=day_end_utc).count()
            daily_event_data.append({"date": local_day_start.strftime("%Y-%m-%d"), "events": daily_events})

        # Adjust the initial current_week_end to the first Saturday of the year
        current_week_start = start_of_year_utc
        current_week_end = start_of_year_utc + timedelta(days=(5 - start_of_year_utc.weekday()) % 7)
        current_week_end = current_week_end.replace(hour=23, minute=59, second=59)  # Set time to the end of Saturday
        total_events = 0
        weeks_count = 0
        while current_week_start < end_of_year_utc:

            weekly_events = Event.objects.filter(user=user, start_time__gte=current_week_start, start_time__lt=current_week_end).count()
            total_events += weekly_events
            weeks_count += 1
            weekly_event_data.append([weekly_events, current_week_start.date(), current_week_end.date()])

            # Move to the next Sunday
            current_week_start = current_week_end + timedelta(days=1)
            
            # Move to the following Saturday
            current_week_end = (current_week_start + timedelta(days=6)).replace(hour=23, minute=59, second=59)
            
            # Ensure the last week ends on Dec 31st
            if current_week_end > end_of_year_utc:
                current_week_end = end_of_year_utc

        weekly_average = total_events / weeks_count if weeks_count > 0 else 0

        for month in range(1, end_of_year_utc.month + 1):  
            if month == end_of_year_utc.month:
                end_of_month_utc = end_of_year_utc
            else:
                end_of_month_utc = start_of_month_utc + relativedelta(months=1) - timedelta(seconds=1)

            month_name = start_of_month_utc.strftime("%B")

            monthly_events = Event.objects.filter(user=user, start_time__gte=start_of_month_utc, start_time__lt=end_of_month_utc).count()
            monthly_event_data.append({"month": month_name, "events": monthly_events})

            start_of_month_utc = end_of_month_utc + timedelta(seconds=1)

        data = {
            'daily_average': daily_average,
            'weekly_average': weekly_average,
            'monthly_average': monthly_average,
            'weekly_event_data': weekly_event_data,
            'daily_event_data': daily_event_data,
            'monthly_event_data': monthly_event_data
        }

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)

def yearly_task_completion_data(request, year):
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

        task_histories = TaskHistory.objects.filter(user=user, created_at__gte=start_of_year_utc, created_at__lt=end_of_year_utc)

        daily_task_histories = task_histories.filter(frequency='D')
        weekly_task_histories = task_histories.filter(frequency='W')
        monthly_task_histories = task_histories.filter(frequency='M')

        daily_task_data = []
        weekly_task_data = []
        monthly_task_data = []

        # Compute daily task completion rates
        for day in range((end_of_year_utc - start_of_year_utc).days + 1):
            day_start_utc = start_of_year_utc + timedelta(days=day)
            day_end_utc = day_start_utc + timedelta(days=1, seconds=-1)

            daily_tasks_for_day = daily_task_histories.filter(created_at__gte=day_start_utc, created_at__lt=day_end_utc)

            daily_tasks_completed = daily_tasks_for_day.filter(status=True).count()
            total_daily_tasks = daily_tasks_for_day.count()
            completion_rate = daily_tasks_completed / total_daily_tasks * 100 if total_daily_tasks != 0 else 0

            daily_task_data.append({
                'date': day_start_utc.date(),
                'completion_rate': completion_rate,
                'ratio': f"{daily_tasks_completed}/{total_daily_tasks}",
                'total_tasks': total_daily_tasks,
                'completed': daily_tasks_completed,
                'incompleted': total_daily_tasks - daily_tasks_completed,
            })

        # Compute weekly task completion rates
        print(f"start of year (UTC): {start_of_year_utc}, end of year (UTC): {end_of_year_utc}")

        current_week_start = start_of_year_utc
        current_week_end = start_of_year_utc + timedelta(days=(5 - start_of_year_utc.weekday()) % 7)
        current_week_end = current_week_end.replace(hour=23, minute=59, second=59)  # Set time to the end of Saturday
        while current_week_start < end_of_year_utc:

            weekly_tasks_for_week = weekly_task_histories.filter(created_at__gte=current_week_start, created_at__lte=current_week_end)
            weekly_tasks_completed = weekly_tasks_for_week.filter(status=True).count()
            total_weekly_tasks = weekly_tasks_for_week.count()
            completion_rate = weekly_tasks_completed / total_weekly_tasks * 100 if total_weekly_tasks != 0 else 0

            weekly_task_data.append({
                'date': f"{current_week_start.date()} - {current_week_end.date()}",
                'completion_rate': completion_rate,
                'ratio': f"{weekly_tasks_completed}/{total_weekly_tasks}",
                'total_tasks': total_weekly_tasks,
                'completed': weekly_tasks_completed,
                'incompleted': total_weekly_tasks - weekly_tasks_completed,
            })

            current_week_start = current_week_end + timedelta(days=1)
            current_week_end = (current_week_start + relativedelta(days=6)).replace(hour=23, minute=59, second=59) # Move to the following Saturday
            # Ensure the last week ends on Dec 31st
            if current_week_end > end_of_year_utc:
                current_week_end = end_of_year_utc

        # Compute monthly task completion rates
        for month in range(1, 13):
            month_start_utc = utc.localize(datetime(year, month, 1))
            month_end_utc = (month_start_utc + relativedelta(months=1)) - timedelta(seconds=1)

            monthly_tasks_for_month = monthly_task_histories.filter(created_at__gte=month_start_utc, created_at__lt=month_end_utc)
            monthly_tasks_completed = monthly_tasks_for_month.filter(status=True).count()
            total_monthly_tasks = monthly_tasks_for_month.count()
            completion_rate = monthly_tasks_completed / total_monthly_tasks * 100 if total_monthly_tasks != 0 else 0

            monthly_task_data.append({
                'month': month_start_utc.strftime("%B"),
                'completion_rate': completion_rate,
                'ratio': f"{monthly_tasks_completed}/{total_monthly_tasks}",
                'total_tasks': total_monthly_tasks,
                'completed': monthly_tasks_completed,
                'incompleted': total_monthly_tasks - monthly_tasks_completed
            })

        data = {
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