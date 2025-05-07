from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import Task, ThanksMessage
from .serializers import TaskSerializer, TaskDetailSerializer, ThanksMessageSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    """List all tasks or create a new task."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter tasks by status if provided."""
        queryset = Task.objects.all()
        status = self.request.query_params.get('status')
        
        if status:
            queryset = queryset.filter(status=status)
        
        # Only show tasks that haven't passed their time
        return queryset.filter(time__gte=timezone.now())
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        return context


class TaskDetailView(generics.RetrieveAPIView):
    """Retrieve a specific task."""
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskTakeView(APIView):
    """Take a task."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if task can be taken
        if task.status != Task.TaskStatus.OPEN:
            return Response(
                {"error": "Task is not available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the poster
        if request.user == task.poster:
            return Response(
                {"error": "You cannot take your own task"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Take the task
        success = task.take(request.user)
        
        if success:
            serializer = TaskDetailSerializer(task)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Failed to take task"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class TaskCompleteView(APIView):
    """Mark a task as completed."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is the taker
        if request.user != task.taker:
            return Response(
                {"error": "Only the task taker can mark it as completed"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Complete the task
        success = task.complete()
        
        if success:
            serializer = TaskDetailSerializer(task)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Failed to complete task"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ThanksMessageCreateView(generics.CreateAPIView):
    """Create a thank you message for a completed task."""
    serializer_class = ThanksMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        return context


class UserTasksView(generics.ListAPIView):
    """List tasks posted or taken by the current user."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter tasks by user role and status."""
        user = self.request.user
        role = self.request.query_params.get('role', 'all')
        status_param = self.request.query_params.get('status')
        
        if role == 'poster':
            queryset = Task.objects.filter(poster=user)
        elif role == 'taker':
            queryset = Task.objects.filter(taker=user)
        else:
            # Both posted and taken tasks
            queryset = Task.objects.filter(poster=user) | Task.objects.filter(taker=user)
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset.order_by('-updated_at')


class NearbyTasksView(generics.ListAPIView):
    """
    List tasks near the user's location.
    
    Note: This is a simplified implementation. In a real application,
    you would use geographic coordinates and proper distance calculations.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter tasks by location keyword.
        
        In a real implementation, this would use geographic coordinates.
        """
        location = self.request.query_params.get('location', '')
        
        # Filter by open status and location (simplified)
        queryset = Task.objects.filter(
            status=Task.TaskStatus.OPEN,
            time__gte=timezone.now()
        )
        
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset.order_by('time')