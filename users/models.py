from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Custom user manager for LINE-based User model."""
    
    def create_user(self, line_id, display_name, password=None, **extra_fields):
        """Create and save a regular user."""
        if not line_id:
            raise ValueError('Users must have a LINE ID')
        
        user = self.model(line_id=line_id, display_name=display_name, **extra_fields)
        user.set_password(password)  # LINE-based auth won't use this, but needed for admin
        user.save(using=self._db)
        return user
    
    def create_superuser(self, line_id, display_name, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(line_id, display_name, password, **extra_fields)


class User(AbstractUser):
    """User model for MeowTask. Uses LINE ID for authentication."""
    
    # Set USERNAME_FIELD to line_id for authentication
    USERNAME_FIELD = 'line_id'
    REQUIRED_FIELDS = ['display_name']
    
    # Make username field nullable as we're using line_id instead
    username = models.CharField(max_length=150, blank=True, null=True)
    
    # LINE-specific fields
    line_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    picture_url = models.URLField(blank=True, null=True)
    
    # Experience/level system
    level = models.PositiveIntegerField(default=1)
    exp = models.PositiveIntegerField(default=0)
    completed_tasks = models.PositiveIntegerField(default=0)
    
    objects = UserManager()
    
    def __str__(self):
        return self.display_name
    
    def add_exp(self, amount):
        """Add experience points and level up if necessary."""
        self.exp += amount
        
        # Simple level-up logic: 100 * current level = exp needed to level up
        exp_needed = self.level * 100
        
        if self.exp >= exp_needed:
            self.level += 1
            self.exp -= exp_needed
            return True  # Indicates level up occurred
        
        return False
    
    def complete_task(self, task):
        """Mark a task as completed and gain experience."""
        self.completed_tasks += 1
        did_level_up = self.add_exp(task.reward)
        self.save()
        return did_level_up