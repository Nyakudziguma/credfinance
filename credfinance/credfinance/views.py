from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import inflect
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDay
from chat.models import Client  
from bwm.models import MessageResponse

@login_required
def home(request):
    today = datetime.now()
    p = inflect.engine()
    day_ordinal = p.ordinal(today.day)  
    weekday = today.strftime("%A")  
    formatted_date = today.strftime(f"{day_ordinal} %B, %Y")

    start_of_week = today - timedelta(days=today.weekday()) 
    end_of_week = start_of_week + timedelta(days=6)  #
    start_of_last_week = start_of_week - timedelta(days=7)  
    end_of_last_week = start_of_week - timedelta(days=1)  
    # Query for the current week
    current_week_data = (
        Client.objects.filter(
            created_at__date__gte=start_of_week, 
            created_at__date__lte=end_of_week
        )
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
    )

    # Query for the last week
    last_week_data = (
        Client.objects.filter(
            created_at__date__gte=start_of_last_week, 
            created_at__date__lte=end_of_last_week
        )
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
    )

    # Prepare data for chart
    def get_weekly_data(week_data, start_date):
        day_counts = {start_date + timedelta(days=i): 0 for i in range(7)}
        for entry in week_data:
            day_counts[entry['day']] = entry['count']
        return list(day_counts.values())

    current_week_counts = get_weekly_data(current_week_data, start_of_week)
    last_week_counts = get_weekly_data(last_week_data, start_of_last_week)

    total_current_week = sum(current_week_counts)
    total_last_week = sum(last_week_counts)


    client_data = {
        "labels": [1, 2, 3, 4, 5, 6, 7],
        "series": [
            current_week_counts,
            last_week_counts
        ]
    }
    #campaigns
    total_messages = MessageResponse.objects.count()
    successful_messages = MessageResponse.objects.filter(status="Successful").count()
    failed_messages = MessageResponse.objects.filter(status="Failed").count()

    campaign_data = [
        ["Successful", successful_messages],
        ["Failed", failed_messages],
        ["Total", total_messages]
    ]
 

    context = {
        'today_weekday': weekday,
        'today_date': formatted_date,
        "client_data": client_data,
        "campaign_data": campaign_data,
        "total_current_week": total_current_week,  
        "total_last_week": total_last_week,
        "total_messages": total_messages,
        "successful_messages":successful_messages,
        "failed_messages": failed_messages,
    }
  
    return render(request, 'dashboard/main.html', context)
