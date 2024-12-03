from django.db import models
from accounts.models import Company, Account

class CompanyBalance(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="balance")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  

    def __str__(self):
        return f"{self.company.name} - Balance: ${self.balance}"

    def update_balance(self, amount):
        """Update the user's balance."""
        self.balance += amount
        self.save()


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('top_up', 'Credit'),
        ('deduction', 'Debit'),
    ]

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type}: ${self.amount}"

class Prices(models.Model):
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.price}"