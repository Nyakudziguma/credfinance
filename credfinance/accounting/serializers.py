from rest_framework import serializers
from .models import *

class ExpenseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseRequest
        fields = ['id', 'amount', 'purpose', 'request_date', 'requested_by', 'approved', 'approved_by']
        read_only_fields = ['request_date', 'requested_by', 'approved', 'approved_by']

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['amount', 'source', 'date_received', 'description', 'invoice_file', 'income_type']

        read_only_fields = ['added_by', 'date_received']

class QuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = ['vendor_name', 'amount', 'quote_date', 'selected', 'quote_file', 'expense_request']
        read_only_fields = ['added_by', 'quote_date']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'added_by', 'expense_request', 'amount', 'invoice_date', 'vendor_name', 'invoice_file']
        read_only_fields = ['added_by', 'expense_request', 'invoice_date'] 

class ProofOfPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofOfPayment
        fields = ['id', 'added_by', 'expense_request', 'payment_date', 'payment_file', 'transaction_id', 'payment_method']
        read_only_fields = ['added_by', 'expense_request']  
