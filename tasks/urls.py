from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/take/', views.TaskTakeView.as_view(), name='task-take'),
    path('<int:pk>/complete/', views.TaskCompleteView.as_view(), name='task-complete'),
    path('thanks/', views.ThanksMessageCreateView.as_view(), name='thanks-create'),
    path('my-tasks/', views.UserTasksView.as_view(), name='user-tasks'),
    path('nearby/', views.NearbyTasksView.as_view(), name='nearby-tasks'),
]