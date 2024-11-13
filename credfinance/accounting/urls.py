from django.urls import path
from .views import *

urlpatterns = [
    path('expenses/', ExpenseRequestAPIView.as_view(), name='expense-request'),
    path('income/', IncomeAPIView.as_view(), name='income'),
    path('quotations/', QuotationAPIView.as_view(), name='quotation'),
    path('invoice/', InvoiceAPIView.as_view(), name='invoice'),
    path('proof_of_payment/', ProofOfPaymentAPIView.as_view(), name='proof-of-payment'),
    
]