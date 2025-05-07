from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<str:line_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
]