from django.contrib import admin
from .models import Taskboard

@admin.register(Taskboard)
class TaskboardAdmin(admin.ModelAdmin):
    list_display = [i.name for i in Taskboard._meta.fields]
