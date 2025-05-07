from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('line_id', 'display_name', 'level', 'exp', 'completed_tasks')
    list_filter = ('level',)
    search_fields = ('line_id', 'display_name')
    ordering = ('display_name',)
    
    fieldsets = (
        (None, {'fields': ('line_id', 'display_name')}),
        ('Profile', {'fields': ('picture_url',)}),
        ('Stats', {'fields': ('level', 'exp', 'completed_tasks')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('line_id', 'display_name', 'password1', 'password2'),
        }),
    )