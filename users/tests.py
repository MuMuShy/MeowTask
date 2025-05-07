from django.test import TestCase
from .models import User


class UserModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            line_id='test_line_id',
            display_name='Test User'
        )
    
    def test_add_exp_no_level_up(self):
        """Test adding exp without triggering level up."""
        self.user.level = 1
        self.user.exp = 0
        
        level_up = self.user.add_exp(50)
        
        self.assertEqual(self.user.exp, 50)
        self.assertEqual(self.user.level, 1)
        self.assertFalse(level_up)
    
    def test_add_exp_with_level_up(self):
        """Test adding exp with level up."""
        self.user.level = 1
        self.user.exp = 80
        
        level_up = self.user.add_exp(30)
        
        self.assertEqual(self.user.exp, 10)  # 80 + 30 - 100 = 10
        self.assertEqual(self.user.level, 2)
        self.assertTrue(level_up)
    
    def test_add_exp_multiple_level_ups(self):
        """Test adding exp with multiple level ups."""
        self.user.level = 1
        self.user.exp = 0
        
        level_up = self.user.add_exp(250)  # Enough for 2 level ups and 50 exp
        
        self.assertEqual(self.user.exp, 50)
        self.assertEqual(self.user.level, 3)
        self.assertTrue(level_up)