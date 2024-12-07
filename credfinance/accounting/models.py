from django.db import models
from django.utils import timezone
from accounts.models import Account
import uuid

class Income(models.Model):
    added_by = models.ForeignKey(Account,on_delete=models.CASCADE )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=100)
    date_received = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    income_slip = models.FileField(upload_to='income/', blank=True, null=True)
    INCOME_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ]
    income_type = models.CharField(max_length=10, choices=INCOME_TYPE_CHOICES)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class ExpenseRequest(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.CharField(max_length=255)
    request_date = models.DateField(default=timezone.now)
    requested_by = models.ForeignKey(Account,on_delete=models.CASCADE, related_name='expense_request' )
    status = models.CharField(default='Pending', max_length=100)
    approved_by = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null = True )
    rejection_reason = models.CharField(blank=True, null = True, max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_approved = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.purpose} - {self.amount}"

class Quotation(models.Model):
    added_by = models.ForeignKey(Account,on_delete=models.CASCADE )
    expense_request = models.ForeignKey(ExpenseRequest, on_delete=models.CASCADE, related_name='quotations')
    vendor_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    quote_date = models.DateField(default=timezone.now)
    status = models.CharField(default='Pending', max_length=100)
    quote_file = models.FileField(upload_to='quotations/', blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class Invoice(models.Model):
    added_by = models.ForeignKey(Account,on_delete=models.CASCADE )
    expense_request = models.ForeignKey(ExpenseRequest, on_delete=models.CASCADE, related_name='invoice')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    invoice_date = models.DateField(default=timezone.now)
    vendor_name = models.CharField(max_length=100)
    invoice_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class ProofOfPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ]
    added_by = models.ForeignKey(Account,on_delete=models.CASCADE )
    expense_request = models.ForeignKey(ExpenseRequest, on_delete=models.CASCADE, related_name='proof_of_payment')
    payment_date = models.DateField(default=timezone.now)
    payment_file = models.FileField(upload_to='proof_of_payment/')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)  
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Transaction(models.Model):
    expense_request = models.ForeignKey(ExpenseRequest, on_delete=models.CASCADE, blank=True, null=True)
    income = models.ForeignKey(Income, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    debit_account = models.CharField(max_length=100)  
    credit_account = models.CharField(max_length=100)  
    transaction_date = models.DateField(default=timezone.now)
    description = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
