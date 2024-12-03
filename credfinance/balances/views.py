from django.shortcuts import render
from .models import Transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

@login_required
def transactions(request,):
    responses = Transaction.objects.all().order_by('-created_at')  #
    paginator = Paginator(responses, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'apps/transactions.html', {'page_obj': page_obj})
