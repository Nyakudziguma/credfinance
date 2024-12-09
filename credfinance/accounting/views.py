from django.shortcuts import render
from .models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import JsonResponse

@login_required
def expense_requests(request,):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    responses = ExpenseRequest.objects.all().order_by('-request_date')  
    paginator = Paginator(responses, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounting/requests.html', {'page_obj': page_obj})


@login_required
def approve_request(request, uuid):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    if request.user.user_type == 'finance_manager':
        expense_request = get_object_or_404(ExpenseRequest, uuid=uuid)
        expense_request.status = 'Approved'
        expense_request.approved_by = request.user
        expense_request.date_approved = timezone.now()
        expense_request.save()
        messages.success(request, "Expense request has been approved!")

        
        email_subject = "Expense Request Approved"
        email_body = (
            f"Hi {expense_request.requested_by.first_name},\n\n"
            f"Your expense request has been approved:\n\n"
            f"Request ID: {expense_request.uuid}\n"
            f"Purpose: {expense_request.purpose}\n"
            f"Approved By: {expense_request.approved_by.first_name}\n"
            f"Date Approved: {expense_request.date_approved}\n\n"
            f"Thank you!"
        )

        email = EmailMessage(
            email_subject,
            email_body,
            to=[expense_request.requested_by.email]
        )

        try:
            email.send()
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error sending email: {str(e)}'})

        return redirect('expense_requests')  

    return redirect('home')  

@login_required
def reject_request(request, uuid):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    if request.user.user_type == 'finance_manager':
        expense_request = get_object_or_404(ExpenseRequest, uuid=uuid)
        if request.method == 'POST':
            rejection_reason = request.POST.get('rejection_reason')
            expense_request.status = 'Rejected'
            expense_request.approved_by = request.user
            expense_request.rejection_reason = rejection_reason
            expense_request.date_approved = timezone.now()
            expense_request.save()

            messages.success(request, "Expense request has been rejected!")

            email_subject = "Expense Request Rejected"
            email_body = (
                f"Hi {expense_request.requested_by.first_name},\n\n"
                f"Your expense request has been rejected:\n\n"
                f"Request ID: {expense_request.uuid}\n"
                f"Purpose: {expense_request.purpose}\n"
                f"Rejected By: {expense_request.approved_by.first_name}\n"
                f"Date Rejected: {expense_request.date_approved}\n\n"
                f"Rejection Reason: {expense_request.rejection_reason}\n\n"
                f"Thank you!"
            )

            email = EmailMessage(
                email_subject,
                email_body,
                to=[expense_request.requested_by.email]
            )

            try:
                email.send()
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error sending email: {str(e)}'})

            return redirect('expense_requests')  
        else:
            return redirect('home')  

    return redirect('home')  

@login_required
def add_request(request):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    if request.method == 'POST':
        amount = request.POST.get('amount')
        purpose = request.POST.get('purpose')
        
        ExpenseRequest.objects.create(
            amount=amount,
            purpose=purpose,
            requested_by=request.user,
            status='Pending',
            request_date=timezone.now()
        )
        messages.success(request, "Your expense request has been submitted!")
        return redirect('expense_requests')
    
    return redirect('home')

@login_required
def income(request,):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    responses = Income.objects.all().order_by('-date_received')  
    paginator = Paginator(responses, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounting/income.html', {'page_obj': page_obj})


@login_required
def add_income(request):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    if request.method == 'POST':
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        income_type = request.POST.get('income_type')
        date_received = request.POST.get('date_received')
        description = request.POST.get('description', '')
        income_slip = request.FILES.get('income_slip', None)

        Income.objects.create(
            added_by=request.user,
            amount=amount,
            source=source,
            income_type=income_type,
            date_received=date_received,
            description=description,
            income_slip=income_slip,
        )
        messages.success(request, "Income added successfully")
        return redirect('income')  
    return redirect('home') 

@login_required
def quotations(request,):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    
    responses = Quotation.objects.all().order_by('-quote_date')  
    paginator = Paginator(responses, 10)  
    page_number = request.GET.get('page')

    expense_requests = ExpenseRequest.objects.all()
    page_obj = paginator.get_page(page_number)
    context = {
        'expense_requests': expense_requests,
        'page_obj': page_obj
    }
    
    if request.method == "POST":
        expense_request_id = request.POST.get("expense_request")
        vendor_name = request.POST.get("vendor_name")
        amount = request.POST.get("amount")
        quote_type = request.POST.get("Quotation_type")
        quote_date = request.POST.get("quote_date")
        quote_file = request.FILES.get("quote_file")

        try:
            expense_request = ExpenseRequest.objects.get(id=expense_request_id)
        except ExpenseRequest.DoesNotExist:
            messages.error(request, "Selected Expense Request does not exist.")
            return redirect("quotations") 
        quotation = Quotation(
            expense_request=expense_request,
            vendor_name=vendor_name,
            amount=amount,
            status="Pending",  
            quote_date=quote_date,
            quote_file=quote_file,
            added_by=request.user,  
        )

        quotation.save()

        messages.success(request, "Quotation added successfully!")
        return redirect("quotations") 
    return render(request, 'accounting/quotations.html', context)
    
@login_required
def invoices(request,):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    
    responses = Invoice.objects.all().order_by('-invoice_date')  
    paginator = Paginator(responses, 10)  
    page_number = request.GET.get('page')

    expense_requests = ExpenseRequest.objects.all()
    page_obj = paginator.get_page(page_number)
    context = {
        'expense_requests': expense_requests,
        'page_obj': page_obj
    }
    
    if request.method == "POST":
        expense_request_id = request.POST.get("expense_request")
        vendor_name = request.POST.get("vendor_name")
        amount = request.POST.get("amount")
        invoice_date = request.POST.get("invoice_date")
        invoice_file = request.FILES.get("invoice_file")

        try:
            expense_request = ExpenseRequest.objects.get(id=expense_request_id)
        except ExpenseRequest.DoesNotExist:
            messages.error(request, "Selected Expense Request does not exist.")
            return redirect("quotations") 
        invoice = Invoice(
            expense_request=expense_request,
            vendor_name=vendor_name,
            amount=amount,
            invoice_date=invoice_date,
            invoice_file=invoice_file,
            added_by=request.user,  
        )

        invoice.save()

        messages.success(request, "Invoice added successfully!")
        return redirect("invoices") 
    return render(request, 'accounting/invoices.html', context)
    
  
@login_required
def pops(request,):
    if request.user.user_type == 'general_user':
        messages.error(request, "You do not have permissions to access this page")
        return redirect('home')
    
    responses = ProofOfPayment.objects.all().order_by('-payment_date')  
    paginator = Paginator(responses, 10)  
    page_number = request.GET.get('page')

    expense_requests = ExpenseRequest.objects.all()
    page_obj = paginator.get_page(page_number)
    context = {
        'expense_requests': expense_requests,
        'page_obj': page_obj
    }
    
    if request.method == "POST":
        expense_request_id = request.POST.get("expense_request")
        payment_date = request.POST.get("payment_date")
        payment_method = request.POST.get("payment_method")
        payment_file = request.FILES.get("payment_file")

        try:
            expense_request = ExpenseRequest.objects.get(id=expense_request_id)
        except ExpenseRequest.DoesNotExist:
            messages.error(request, "Selected Expense Request does not exist.")
            return redirect("quotations") 
        pop = ProofOfPayment(
            expense_request=expense_request,
            payment_date=payment_date,
            payment_method=payment_method,
            payment_file=payment_file,
            added_by=request.user,  
        )

        pop.save()

        messages.success(request, "POP added successfully!")
        return redirect("pops") 
    return render(request, 'accounting/pops.html', context)
    