from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class AccountAdmin(UserAdmin):
    list_display = [i.name for i in Account._meta.fields]
    list_display_links= ('email', 'first_name','last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-last_name',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
