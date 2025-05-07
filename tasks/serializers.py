from rest_framework import serializers
from .models import Task, ThanksMessage
from users.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for the Task model."""
    
    poster = UserSerializer(read_only=True)
    taker = UserSerializer(read_only=True)
    poster_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'reward', 'location', 
                 'time', 'status', 'poster', 'taker', 'poster_id',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Remove poster_id from validated_data if present
        poster_id = validated_data.pop('poster_id', None)
        
        # Get the user from the context
        user = self.context['request'].user
        
        # Create the task with the current user as poster
        task = Task.objects.create(poster=user, **validated_data)
        return task


class ThanksMessageSerializer(serializers.ModelSerializer):
    """Serializer for the ThanksMessage model."""
    
    sender = UserSerializer(read_only=True)
    task_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ThanksMessage
        fields = ['id', 'message', 'task_id', 'task', 'sender', 'created_at']
        read_only_fields = ['id', 'created_at', 'task', 'sender']
    
    def create(self, validated_data):
        task_id = validated_data.pop('task_id')
        user = self.context['request'].user
        
        # Ensure the task exists and is completed
        from .models import Task
        try:
            task = Task.objects.get(id=task_id, status=Task.TaskStatus.DONE)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task not found or not completed")
        
        # Ensure the user is either the poster or taker of the task
        if user != task.poster and user != task.taker:
            raise serializers.ValidationError("You can only send thanks for tasks you're involved in")
        
        # Create the thanks message
        thanks = ThanksMessage.objects.create(
            task=task,
            sender=user,
            **validated_data
        )
        return thanks


class TaskDetailSerializer(TaskSerializer):
    """Detailed serializer for Task including thanks message if available."""
    
    thanks_message = ThanksMessageSerializer(read_only=True)
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['thanks_message']