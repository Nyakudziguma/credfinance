from django.contrib import admin
from .models import Intent, Pattern, Response

@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'description')
    search_fields = ('tag',)

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ('id', 'intent', 'text')
    search_fields = ('text',)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'intent', 'text')
    search_fields = ('text',)
