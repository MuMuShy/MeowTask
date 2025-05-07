from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from users.models import User
from tasks.models import Task
import json


class LineWebhookTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('linebot:webhook')
        
        # Create a test user
        self.user = User.objects.create(
            line_id='test_line_id',
            display_name='Test User'
        )
        
        # Create a test task
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            reward=10,
            location='Test Location',
            time='2025-12-31T12:00:00Z',
            poster=self.user
        )
    
    @patch('linebot.line_bot_handler.handle_webhook')
    def test_webhook_endpoint(self, mock_handle_webhook):
        """Test the LINE webhook endpoint."""
        mock_handle_webhook.return_value = True
        
        # Test data
        webhook_data = {
            'events': [
                {
                    'type': 'message',
                    'message': {'type': 'text', 'text': 'help'},
                    'source': {'type': 'user', 'userId': 'test_line_id'}
                }
            ]
        }
        
        # Set up the signature header
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type='application/json',
            HTTP_X_LINE_SIGNATURE='signature'
        )
        
        # Check that the handler was called
        mock_handle_webhook.assert_called_once()
        
        # Check response
        self.assertEqual(response.status_code, 200)