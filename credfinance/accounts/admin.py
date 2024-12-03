from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.html import format_html


class AccountAdmin(UserAdmin):
    list_display = [i.name for i in Account._meta.fields]
    list_display_links= ('email', 'first_name','last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-last_name',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [i.name for i in Company._meta.fields]

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = [i.name for i in CompanyProfile._meta.fields]

@admin.register(CompanyAuthentication)
class CompanyAuthenticationAdmin(admin.ModelAdmin):
    list_display = [i.name for i in CompanyAuthentication._meta.fields]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src = "{}" width="30" style="border-radius:50%,">'.format(object.profile_picture.url))
    thumbnail.short_description = "Profile Picture"
    list_display = ('thumbnail', 'user',)