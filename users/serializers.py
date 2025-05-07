from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    class Meta:
        model = User
        fields = ['id', 'line_id', 'display_name', 'picture_url', 
                 'level', 'exp', 'completed_tasks']
        read_only_fields = ['id', 'level', 'exp', 'completed_tasks']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with additional calculated fields."""
    
    next_level_exp = serializers.SerializerMethodField()
    exp_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'display_name', 'picture_url', 'level', 'exp', 
                 'completed_tasks', 'next_level_exp', 'exp_percentage']
    
    def get_next_level_exp(self, obj):
        """Get experience needed for next level."""
        return obj.level * 100
    
    def get_exp_percentage(self, obj):
        """Get percentage progress to next level."""
        next_level_exp = obj.level * 100
        if next_level_exp == 0:  # Avoid division by zero
            return 100
        return int((obj.exp / next_level_exp) * 100)