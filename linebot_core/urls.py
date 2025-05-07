from django.urls import path
from . import views

app_name = 'linebot'

urlpatterns = [
    path('line/', views.line_webhook, name='webhook'),
]