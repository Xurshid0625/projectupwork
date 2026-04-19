from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile


class CustomUserAdmin(UserAdmin):
    model = User
    
    list_display = ('username', 'email', 'role', 'is_staff')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('full_name', 'role')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('full_name', 'role')}),
    )
    
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
