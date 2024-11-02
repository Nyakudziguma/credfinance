
from django.contrib import admin
from .models import *


@admin.register(AuditTrail)
class CompanyTrailAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'model_id', 'timestamp', 'ip_address')
    list_filter = ('user', 'action', 'model_name', 'timestamp')
    search_fields = ('action', 'model_name', 'user__username')