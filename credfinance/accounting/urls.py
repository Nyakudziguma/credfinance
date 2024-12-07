from django.urls import path
from .views import *

urlpatterns = [
    path('expense-request/', expense_requests , name='expense_requests'),
    path('approve_request/<uuid:uuid>/', approve_request, name='approve_request'),
    path('reject_request/<uuid:uuid>/', reject_request, name='reject_request'),
    path('add_request/', add_request, name='add_request'),
    path('income/', income, name='income'),
    path('add_income/', add_income, name='add_income'),
    path('quotations/', quotations, name='quotations'),
    path('invoices/', invoices, name='invoices'),
    path('pops/', pops, name='pops'),
]