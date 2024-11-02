from django.db import models
from accounts.models import Account

class AuditTrail(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    model_id = models.IntegerField(null=True, blank=True)
    previous_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    def __str__(self):
        return f"{self.user} - {self.action} on {self.model_name} ({self.model_id})"