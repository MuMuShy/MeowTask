from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, UserProfileSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """Retrieve a user by LINE ID."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'line_id'
    permission_classes = [permissions.IsAuthenticated]


class LeaderboardView(APIView):
    """Get top users by level and experience."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get top 10 users sorted by level (descending) and exp (descending)
        top_users = User.objects.all().order_by('-level', '-exp')[:10]
        serializer = UserSerializer(top_users, many=True)
        
        # Get requesting user's rank
        user = request.user
        user_rank = User.objects.filter(
            level__gt=user.level
        ).count() + User.objects.filter(
            level=user.level, 
            exp__gt=user.exp
        ).count() + 1  # +1 because ranks start at 1
        
        return Response({
            'leaderboard': serializer.data,
            'user_rank': user_rank
        })