import json
import logging
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .line_bot_handler import handle_webhook

logger = logging.getLogger(__name__)


@csrf_exempt
def line_webhook(request):
    """Handle LINE Messaging API webhook."""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST requests are allowed')
    
    # Get X-Line-Signature header value
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        return HttpResponseBadRequest('X-Line-Signature header is missing')
    
    # Get request body
    request_body = request.body.decode('utf-8')
    
    # Log the event for debugging
    logger.debug(f"LINE Webhook: {request_body}")
    
    # Handle webhook events
    result = handle_webhook(request_body, signature)
    
    if result:
        return HttpResponse('OK')
    else:
        return HttpResponseBadRequest('Failed to handle webhook')