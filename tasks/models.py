from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    """Model representing a task that can be posted and accepted by users."""
    
    class TaskStatus(models.TextChoices):
        OPEN = 'open', _('Open')
        TAKEN = 'taken', _('Taken')
        DONE = 'done', _('Done')
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    reward = models.PositiveIntegerField(default=10)
    location = models.CharField(max_length=200)
    time = models.DateTimeField()
    
    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='posted_tasks'
    )
    taker = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        related_name='taken_tasks',
        blank=True, 
        null=True
    )
    
    status = models.CharField(
        max_length=10,
        choices=TaskStatus.choices,
        default=TaskStatus.OPEN
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time']
    
    def __str__(self):
        return self.title
    
    def take(self, user):
        """Mark the task as taken by a user."""
        if self.status != self.TaskStatus.OPEN:
            return False
        
        self.taker = user
        self.status = self.TaskStatus.TAKEN
        self.save()
        return True
    
    def complete(self):
        """Mark the task as completed."""
        if self.status != self.TaskStatus.TAKEN or not self.taker:
            return False
        
        self.status = self.TaskStatus.DONE
        self.save()
        
        # Add exp and update completed_tasks count for the taker
        self.taker.complete_task(self)
        
        return True


class ThanksMessage(models.Model):
    """Model representing a thank you message for a completed task."""
    
    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='thanks_message'
    )
    message = models.TextField()
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_thanks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Thanks for {self.task.title}"