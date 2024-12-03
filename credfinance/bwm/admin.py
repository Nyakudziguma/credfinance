from django.contrib import admin
from .models import BulkMessages, MessageResponse, Templates

@admin.register(BulkMessages)
class BulkMessageAdmin(admin.ModelAdmin):
    list_display = [i.name for i in BulkMessages._meta.fields]
  
@admin.register(MessageResponse)
class MessageResponseAdmin(admin.ModelAdmin):
    list_display = [i.name for i in MessageResponse._meta.fields]
  
@admin.register(Templates)
class TemplatesAdmin(admin.ModelAdmin):
    list_display = [i.name for i in Templates._meta.fields]
  