from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BulkMessageForm
from .tasks import process_csv_file
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator
import csv
from balances.models import *
from django.contrib.auth.decorators import login_required

@login_required
def bulk_messaging(request,):
    responses = MessageResponse.objects.all().order_by('-created_at')  #
    paginator = Paginator(responses, 100)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'apps/bulk-messaging.html', {'page_obj': page_obj})



@login_required
def send_messages(request):
    try:
        price = Prices.objects.get(code='BWM01')
        COST_PER_MESSAGE = price.price
    except Prices.DoesNotExist:
        pass
    if request.method == 'POST':
        form = BulkMessageForm(request.POST, request.FILES)
        if form.is_valid():
            bulk_message = form.save(commit=False)
            bulk_message.user = request.user  
            csv_file = request.FILES['csv']

            try:
                csv_file.seek(0)  
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(decoded_file)
                phone_numbers = [row['phoneNumber'] for row in csv_reader if row.get('phoneNumber')]

                total_numbers = len(phone_numbers)
                total_cost = total_numbers * COST_PER_MESSAGE

                company_balance = CompanyBalance.objects.get(company=request.user.company)
                print(company_balance)

                if company_balance.balance < total_cost:
                    messages.error(request, f"Insufficient balance. You need ${total_cost:.2f}, but your balance is only ${company_balance.balance:.2f}.")
                    return redirect('send_messages')

                bulk_message.save()
                process_csv_file.delay(bulk_message.id)

                messages.success(request, "Your bulk message request is being processed!")
                return redirect('send_messages')

            except Exception as e:
                messages.error(request, f"Error reading CSV file: {e}")
                return redirect('send_messages')
        else:
            messages.error(request, "There was an error in your submission.")
    else:
        form = BulkMessageForm()
    
    templates = Templates.objects.all()
    return render(request, 'apps/send-bulk-messages.html', {'form': form, 'templates': templates})
