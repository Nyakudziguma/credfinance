# admin.py
from django.contrib import admin
from .models import Income, ExpenseRequest, Quotation, Invoice, ProofOfPayment, Transaction

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("id", "added_by", "amount", "source", "date_received", "description")
    list_filter = ("date_received", "source")
    search_fields = ("source", "description")
    readonly_fields = ("date_received",)

@admin.register(ExpenseRequest)
class ExpenseRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "purpose", "request_date", "requested_by", "status", "approved_by")
    list_filter = ("status", "request_date")
    search_fields = ("purpose", "requested_by__username")
    readonly_fields = ("request_date",)

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("id", "added_by", "expense_request", "vendor_name", "amount", "quote_date", "status")
    list_filter = ("quote_date", "status", "vendor_name")
    search_fields = ("vendor_name",)
    readonly_fields = ("quote_date",)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "added_by", "expense_request", "amount", "invoice_date", "vendor_name")
    list_filter = ("invoice_date", "vendor_name")
    search_fields = ("vendor_name",)
    readonly_fields = ("invoice_date",)

@admin.register(ProofOfPayment)
class ProofOfPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "added_by", "expense_request", "payment_date", "transaction_id")
    list_filter = ("payment_date",)
    search_fields = ("transaction_id",)
    readonly_fields = ("payment_date",)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "expense_request", "income", "amount", "debit_account", "credit_account", "transaction_date", "description")
    list_filter = ("transaction_date", "debit_account", "credit_account")
    search_fields = ("description", "debit_account", "credit_account")
    readonly_fields = ("transaction_date",)

