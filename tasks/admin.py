from django.contrib import admin
from .models import Task, ThanksMessage


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'poster', 'taker', 'reward', 'status', 'time')
    list_filter = ('status', 'time')
    search_fields = ('title', 'description', 'poster__display_name', 'taker__display_name')
    date_hierarchy = 'time'


@admin.register(ThanksMessage)
class ThanksMessageAdmin(admin.ModelAdmin):
    list_display = ('task', 'sender', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'sender__display_name', 'task__title')