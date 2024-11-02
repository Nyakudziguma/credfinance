import datetime
import random
from audit.models import AuditTrail
import base64
from django.conf import settings
from django.db import models
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import date
from rest_framework import permissions


class Utils:

    @staticmethod
    def log_audit_trail(user, action, model_name, model_id, previous_value=None, new_value=None, ip_address=None):
        AuditTrail.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            model_id=model_id,
            previous_value=previous_value,
            new_value=new_value,
            ip_address=ip_address,
        )

    @staticmethod
    def get_transaction_reference(prefix='T'):
        """generating vendor reference
        Args:
            prefix: Prefix to vendor reference
        Returns:
            response: Generated vendor number
        """
        MN = ["JA", 'FB', 'MA', 'AP', 'MY', 'JN', 'JL', 'AG', 'SP', 'OC', 'NV', 'DC']
        created = datetime.datetime.now()
        return f"{prefix if prefix else ''}{created.year}{MN[created.month - 1]}{created.day}{created.second}{random.randint(20000, 99999)}"

    @staticmethod
    def record_expense_transaction(expense_request, debit_account, credit_account, amount, description):
        try:
            with transaction.atomic():
                Transaction.objects.create(
                    expense_request=expense_request,
                    amount=amount,
                    debit_account=debit_account,
                    credit_account=credit_account,
                    transaction_date=date.today(),
                    description=description,
                )

                print("Transaction recorded successfully.")
        
        except Exception as e:
            print(f"Transaction failed: {e}")
            raise  

    @staticmethod
    def record_income_transaction(income, debit_account, credit_account, amount, description):
        try:
            with transaction.atomic():
                Transaction.objects.create(
                    income=income,
                    amount=amount,
                    debit_account=debit_account,
                    credit_account=credit_account,
                    transaction_date=date.today(),
                    description=description,
                )

                print("Transaction recorded successfully.")
        
        except Exception as e:
            print(f"Transaction failed: {e}")
            raise  


class IsFinanceManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'finance_manager'
