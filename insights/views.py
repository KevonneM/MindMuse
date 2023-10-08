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

        if year == timezone.now().year:
            now_utc = timezone.now().astimezone(utc)
            end_of_year_utc = utc.localize(datetime(now_utc.year, now_utc.month, now_utc.day, 23, 59,59))
        else:
            end_of_year_utc = start_of_year_utc + relativedelta(years=1) - timedelta(seconds=1)

        total_events = Event.objects.filter(user=user, start_time__gte=start_of_year_utc, start_time__lt=end_of_year_utc).count()
        days_elapsed = (end_of_year_utc - start_of_year_utc).days + 1
        daily_average = total_events / days_elapsed if days_elapsed > 0 else 0

        start_of_week_utc = start_of_year_utc
        weeks_elapsed = ((end_of_year_utc - start_of_week_utc).days // 7) + 1
        weekly_average = total_events / weeks_elapsed if weeks_elapsed > 0 else 0

        start_of_month_utc = start_of_year_utc
        months_elapsed = (end_of_year_utc.month - start_of_year_utc.month) + (end_of_year_utc.day / calendar.monthrange(year, end_of_year_utc.month)[1])
        monthly_average = total_events / months_elapsed if months_elapsed > 0 else 0

        weekly_event_data = []
        daily_event_data = []
        monthly_event_data = []

        for day in range(days_elapsed):
            day_start_utc = start_of_year_utc + timedelta(days=day)
            day_end_utc = day_start_utc + timedelta(days=1, seconds=-1)

            daily_events = Event.objects.filter(user=user, start_time__gte=day_start_utc, start_time__lt=day_end_utc).count()
            daily_event_data.append(daily_events)

        for week in range(weeks_elapsed):
            end_of_week_utc = start_of_week_utc + timedelta(days=6, hours=23, minutes=59, seconds=59)

            if end_of_week_utc > end_of_year_utc:
                end_of_week_utc = end_of_year_utc

            weekly_events = Event.objects.filter(user=user, start_time__gte=start_of_week_utc, start_time__lt=end_of_week_utc).count()
            weekly_event_data.append([weekly_events, start_of_week_utc.date(), end_of_week_utc.date()])

            start_of_week_utc = end_of_week_utc + timedelta(seconds=1)

        for month in range(1, end_of_year_utc.month + 1):  
            if month == end_of_year_utc.month:
                end_of_month_utc = end_of_year_utc
            else:
                end_of_month_utc = start_of_month_utc + relativedelta(months=1) - timedelta(seconds=1)

            monthly_events = Event.objects.filter(user=user, start_time__gte=start_of_month_utc, start_time__lt=end_of_month_utc).count()
            monthly_event_data.append(monthly_events)

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

        print(f"[DEBUG] Computed End of Year (UTC): {end_of_year_utc}")

        task_histories = TaskHistory.objects.filter(user=user, created_at__gte=start_of_year_utc, created_at__lt=end_of_year_utc)

        print(f"[DEBUG] Tasks fetched from DB: {task_histories.count()}")
        for task in task_histories[:5]:
            print(f"[DEBUG] Task: {task.id}, Created At: {task.created_at}")

        daily_task_histories = task_histories.filter(frequency='D')
        print(f"[INFO] Total daily tasks retrieved: {daily_task_histories.count()}")
        weekly_task_histories = task_histories.filter(frequency='W')
        monthly_task_histories = task_histories.filter(frequency='M')

        daily_task_data = []
        weekly_task_data = []
        monthly_task_data = []

        # Compute daily task completion rates
        for day in range((end_of_year_utc - start_of_year_utc).days + 1):
            day_start_utc = start_of_year_utc + timedelta(days=day)
            day_end_utc = day_start_utc + timedelta(days=1, seconds=-1)

            print(f"[INFO] User timezone: {user.timezone}, for {user.username}")
            print(f"[INFO] Start of Year (UTC):{start_of_year_utc}")
            print(f"[INFO] start of day (UTC):{day_start_utc}")
            print(f"[INFO] end of day (UTC):{day_end_utc}")

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
        for week in range((end_of_year_utc - start_of_year_utc).days // 7 + 1):
            week_start_utc = start_of_year_utc + timedelta(weeks=week)
            week_end_utc = week_start_utc + timedelta(weeks=1, seconds=-1)

            weekly_tasks_for_week = weekly_task_histories.filter(created_at__gte=week_start_utc, created_at__lt=week_end_utc)
            weekly_tasks_completed = weekly_tasks_for_week.filter(status=True).count()
            total_weekly_tasks = weekly_tasks_for_week.count()
            completion_rate = weekly_tasks_completed / total_weekly_tasks * 100 if total_weekly_tasks != 0 else 0

            weekly_task_data.append({
                'date': f"{week_start_utc.astimezone(user_timezone).date()} - {week_end_utc.astimezone(user_timezone).date()}",
                'completion_rate': completion_rate,
                'ratio': f"{weekly_tasks_completed}/{total_weekly_tasks}",
                'total_tasks': total_weekly_tasks,
                'completed': weekly_tasks_completed,
                'incompleted': total_weekly_tasks - weekly_tasks_completed,
            })

        # Compute monthly task completion rates
        for month in range(1, 13):
            month_start_utc = utc.localize(datetime(year, month, 1))
            month_end_utc = (month_start_utc + relativedelta(months=1)) - timedelta(seconds=1)

            monthly_tasks_for_month = monthly_task_histories.filter(created_at__gte=month_start_utc, created_at__lt=month_end_utc)
            monthly_tasks_completed = monthly_tasks_for_month.filter(status=True).count()
            total_monthly_tasks = monthly_tasks_for_month.count()
            completion_rate = monthly_tasks_completed / total_monthly_tasks * 100 if total_monthly_tasks != 0 else 0

            monthly_task_data.append({
                'month': month_start_utc.astimezone(user_timezone).strftime("%B"),
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
        for week in range((end_of_year_utc - start_of_year_utc).days // 7 + 1):
            week_start_utc = start_of_year_utc + timedelta(weeks=week)
            week_end_utc = week_start_utc + timedelta(days=6)

            if week_end_utc > end_of_year_utc:
                week_end_utc = end_of_year_utc

            week_data = {
                'date_range': f"{week_start_utc.date()} - {week_end_utc.date()}",
                'passions': {},
                'categories': {}
            }

            activities_for_week = passion_activities.filter(date__gte=week_start_utc.date(), date__lte=week_end_utc.date())
            
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