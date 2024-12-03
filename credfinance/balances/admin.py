from django.contrib import admin

from django.contrib import admin
from .models import CompanyBalance, Transaction, Prices

@admin.register(CompanyBalance)
class CompanyBalanceAdmin(admin.ModelAdmin):
    list_display = ('company', 'balance')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')

@admin.register(Prices)
class PricesAdmin(admin.ModelAdmin):
    list_display = ('code', 'price', 'description')