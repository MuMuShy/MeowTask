from django.test import TestCase
from django.utils import timezone
from users.models import User
from .models import Task, ThanksMessage


class TaskModelTests(TestCase):
    
    def setUp(self):
        self.poster = User.objects.create(
            line_id='poster_line_id',
            display_name='Poster User'
        )
        self.taker = User.objects.create(
            line_id='taker_line_id',
            display_name='Taker User'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            reward=20,
            location='Test Location',
            time=timezone.now() + timezone.timedelta(days=1),
            poster=self.poster
        )
    
    def test_take_task(self):
        """Test taking an open task."""
        self.assertEqual(self.task.status, Task.TaskStatus.OPEN)
        
        success = self.task.take(self.taker)
        
        self.assertTrue(success)
        self.assertEqual(self.task.status, Task.TaskStatus.TAKEN)
        self.assertEqual(self.task.taker, self.taker)
    
    def test_take_already_taken_task(self):
        """Test attempting to take an already taken task."""
        self.task.status = Task.TaskStatus.TAKEN
        self.task.taker = self.taker
        self.task.save()
        
        another_user = User.objects.create(
            line_id='another_line_id',
            display_name='Another User'
        )
        
        success = self.task.take(another_user)
        
        self.assertFalse(success)
        self.assertEqual(self.task.taker, self.taker)
    
    def test_complete_task(self):
        """Test completing a taken task."""
        self.task.status = Task.TaskStatus.TAKEN
        self.task.taker = self.taker
        self.task.save()
        
        initial_exp = self.taker.exp
        initial_completed = self.taker.completed_tasks
        
        success = self.task.complete()
        
        self.assertTrue(success)
        self.assertEqual(self.task.status, Task.TaskStatus.DONE)
        
        # Refresh taker from database
        self.taker.refresh_from_db()
        self.assertEqual(self.taker.exp, initial_exp + self.task.reward)
        self.assertEqual(self.taker.completed_tasks, initial_completed + 1)