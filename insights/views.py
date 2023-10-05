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
        
        start_of_year = user_timezone.localize(datetime(year, 1, 1, 0, 0, 0))
        start_of_year_utc = start_of_year.astimezone(utc)

        if year == datetime.now().year:
            now = timezone.now().astimezone(user_timezone)
            end_of_year = user_timezone.localize(datetime(now.year, now.month, now.day, 23, 59, 59))
        else:
            end_of_year = start_of_year + relativedelta(years=1) - timedelta(seconds=1)

        end_of_year_utc = end_of_year.astimezone(utc)

        total_events = Event.objects.filter(user=user, start_time__gte=start_of_year_utc, start_time__lt=end_of_year_utc).count()
        days_elapsed = (end_of_year - start_of_year).days + 1
        daily_average = total_events / days_elapsed

        start_of_week = start_of_year
        weeks_elapsed = ((end_of_year - start_of_week).days // 7) + 1
        weekly_average = total_events / weeks_elapsed

        months_elapsed = (end_of_year.month - start_of_year.month) + (end_of_year.day / calendar.monthrange(year, end_of_year.month)[1])
        monthly_average = total_events / months_elapsed

        weekly_event_data = []
        daily_event_data = []
        monthly_event_data = []

        for day in range(days_elapsed):
            day_start = start_of_year + timedelta(days=day)
            day_end = day_start + timedelta(days=1, seconds=-1)
            day_start_utc = day_start.astimezone(utc)
            day_end_utc = day_end.astimezone(utc)

            daily_events = Event.objects.filter(user=user, start_time__gte=day_start_utc, start_time__lt=day_end_utc).count()
            daily_event_data.append(daily_events)

        for week in range(weeks_elapsed):
            end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
            start_of_week_utc = start_of_week.astimezone(utc)

            if end_of_week > end_of_year:
                end_of_week = end_of_year

            end_of_week_utc = end_of_week.astimezone(utc)

            weekly_events = Event.objects.filter(user=user, start_time__gte=start_of_week_utc, start_time__lt=end_of_week_utc).count()
            weekly_event_data.append([weekly_events, start_of_week.date(), end_of_week.date()])

            start_of_week = end_of_week + timedelta(seconds=1)

        for month in range(1, end_of_year.month + 1):  
            if month == end_of_year.month:
                end_of_month = end_of_year
            else:
                end_of_month = user_timezone.localize(datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59))

            end_of_month_utc = end_of_month.astimezone(utc)

            monthly_events = Event.objects.filter(user=user, start_time__gte=start_of_year_utc, start_time__lt=end_of_month_utc).count()
            monthly_event_data.append(monthly_events)

            start_of_year = end_of_month + timedelta(seconds=1)
            start_of_year_utc = start_of_year.astimezone(utc)

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

        start_of_year = user_timezone.localize(datetime(year, 1, 1, 0, 0, 0))
        start_of_year_utc = start_of_year.astimezone(utc)

        if year == datetime.now().year:
            now = timezone.now().astimezone(user_timezone)
            end_of_year = user_timezone.localize(datetime(now.year, now.month, now.day, 23, 59, 59))
        else:
            end_of_year = start_of_year + relativedelta(years=1) - timedelta(seconds=1)

        end_of_year_utc = end_of_year.astimezone(utc)

        task_histories = TaskHistory.objects.filter(user=user, created_at__gte=start_of_year_utc, created_at__lt=end_of_year_utc)

        daily_task_histories = task_histories.filter(frequency='D')
        weekly_task_histories = task_histories.filter(frequency='W')
        monthly_task_histories = task_histories.filter(frequency='M')

        daily_task_data = []
        weekly_task_data = []
        monthly_task_data = []

        # Compute daily task completion rates
        for day in range((end_of_year - start_of_year).days + 1):
            day_start = start_of_year + timedelta(days=day)
            day_end = day_start + timedelta(days=1, seconds=-1)
            day_start_utc = day_start.astimezone(utc)
            day_end_utc = day_end.astimezone(utc)

            daily_tasks_for_day = daily_task_histories.filter(created_at__gte=day_start_utc, created_at__lt=day_end_utc)
            print(f"\nDay: {day_start.date()} - {day_end.date()}")
            print(f"  Total tasks for day: {daily_tasks_for_day.count()}")
            
            daily_tasks_completed = daily_tasks_for_day.filter(status=True).count()
            total_daily_tasks = daily_tasks_for_day.count()
            completion_rate = daily_tasks_completed / total_daily_tasks * 100 if total_daily_tasks != 0 else 0

            daily_task_data.append({
                'date': day_start.date(),
                'completion_rate': completion_rate,
                'ratio': f"{daily_tasks_completed}/{total_daily_tasks}",
                'total_tasks': total_daily_tasks,
                'completed': daily_tasks_completed,
                'incompleted': total_daily_tasks - daily_tasks_completed,
            })

        # Compute weekly task completion rates
        for week in range((end_of_year - start_of_year).days // 7 + 1):
            week_start = start_of_year + timedelta(weeks=week)
            week_end = week_start + timedelta(weeks=1, seconds=-1)
            week_start_utc = week_start.astimezone(utc)
            week_end_utc = week_end.astimezone(utc)

            weekly_tasks_for_week = weekly_task_histories.filter(created_at__gte=week_start_utc, created_at__lt=week_end_utc)
            weekly_tasks_completed = weekly_tasks_for_week.filter(status=True).count()
            total_weekly_tasks = weekly_tasks_for_week.count()
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
        for month in range(1, 13):
            month_start = start_of_year.replace(month=month)
            month_end = (month_start + relativedelta(months=1)) - timedelta(seconds=1)
            month_start_utc = month_start.astimezone(utc)
            month_end_utc = month_end.astimezone(utc)

            monthly_tasks_for_month = monthly_task_histories.filter(created_at__gte=month_start_utc, created_at__lt=month_end_utc)
            monthly_tasks_completed = monthly_tasks_for_month.filter(status=True).count()
            total_monthly_tasks = monthly_tasks_for_month.count()
            completion_rate = monthly_tasks_completed / total_monthly_tasks * 100 if total_monthly_tasks != 0 else 0

            monthly_task_data.append({
                'month': month_start.strftime("%B"),
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

        start_of_year = user_timezone.localize(datetime(year, 1, 1, 0, 0, 0))
        start_of_year_utc = start_of_year.astimezone(utc)

        if year == datetime.now().year:
            now = timezone.now().astimezone(user_timezone)
            end_of_year = user_timezone.localize(datetime(now.year, now.month, now.day, 23, 59, 59))
        else:
            end_of_year = start_of_year + relativedelta(years=1) - timedelta(seconds=1)

        end_of_year_utc = end_of_year.astimezone(utc)

        passion_activities = PassionActivity.objects.filter(passion__user=user, date__gte=start_of_year.date(), date__lte=end_of_year.date())
        weekly_passion_data = []

        # Compute weekly passion activity data
        for week in range((end_of_year - start_of_year).days // 7 + 1):
            week_start_date = start_of_year + timedelta(weeks=week)
            week_end_date = week_start_date + timedelta(days=6)

            if week_end_date > end_of_year:
                week_end_date = end_of_year

            week_data = {
                'date_range': f"{week_start_date.date()} - {week_end_date.date()}",
                'passions': {},
                'categories': {}
            }

            activities_for_week = passion_activities.filter(date__gte=week_start_date.date(), date__lte=week_end_date.date())
            
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

        data = {
            'weekly_passion_data': weekly_passion_data
        }

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)