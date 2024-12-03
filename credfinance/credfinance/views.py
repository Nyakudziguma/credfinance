from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
import inflect


@login_required
def home(request):
    today = datetime.now()
    p = inflect.engine()
    day_ordinal = p.ordinal(today.day)  

    weekday = today.strftime("%A")  

    formatted_date = today.strftime(f"{day_ordinal} %B, %Y")

    context = {
        'today_weekday': weekday,
        'today_date': formatted_date
    }
    return render(request, 'dashboard/main.html', context)
