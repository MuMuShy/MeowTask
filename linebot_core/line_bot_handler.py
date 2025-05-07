import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    TemplateSendMessage, ButtonsTemplate, PostbackAction,
    PostbackEvent, FlexSendMessage
)
from django.conf import settings
from users.models import User
from tasks.models import Task
from django.utils import timezone

logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


def handle_webhook(request_body, signature):
    """Handle LINE webhook events."""
    try:
        handler.handle(request_body, signature)
        return True
    except InvalidSignatureError:
        logger.error("Invalid signature")
        return False
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return False


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """Handle text messages from users."""
    user_id = event.source.user_id
    text = event.message.text.strip().lower()
    
    # Get or create user
    try:
        profile = line_bot_api.get_profile(user_id)
        user, created = User.objects.get_or_create(
            line_id=user_id,
            defaults={
                'display_name': profile.display_name,
                'picture_url': profile.picture_url
            }
        )
        
        # Update profile if not created
        if not created:
            user.display_name = profile.display_name
            user.picture_url = profile.picture_url
            user.save()
    except LineBotApiError as e:
        logger.error(f"LINE API error: {str(e)}")
        return
    
    # Handle commands
    if text == 'help':
        show_help(event.reply_token)
    elif text == 'profile':
        show_profile(event.reply_token, user)
    elif text == 'tasks':
        show_available_tasks(event.reply_token)
    elif text == 'my tasks':
        show_user_tasks(event.reply_token, user)
    elif text.startswith('post:'):
        handle_post_command(event.reply_token, user, text[5:].strip())
    else:
        # Default response
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="I didn't understand that. Type 'help' to see available commands.")
        )


@handler.add(PostbackEvent)
def handle_postback(event):
    """Handle postback events from interactive messages."""
    user_id = event.source.user_id
    data = event.postback.data
    
    try:
        user = User.objects.get(line_id=user_id)
    except User.DoesNotExist:
        logger.error(f"User not found: {user_id}")
        return
    
    # Parse the postback data
    try:
        postback_data = json.loads(data)
        action = postback_data.get('action')
        task_id = postback_data.get('task_id')
    except json.JSONDecodeError:
        logger.error(f"Invalid postback data: {data}")
        return
    
    # Handle different actions
    if action == 'take' and task_id:
        handle_take_task(event.reply_token, user, task_id)
    elif action == 'complete' and task_id:
        handle_complete_task(event.reply_token, user, task_id)
    elif action == 'detail' and task_id:
        show_task_detail(event.reply_token, task_id)


def show_help(reply_token):
    """Show help message with available commands."""
    help_text = (
        "💡 MeowTask Commands 💡\n\n"
        "• help - Show this help message\n"
        "• profile - Show your profile\n"
        "• tasks - Show available tasks\n"
        "• my tasks - Show your tasks\n"
        "• post: [title] - Start posting a new task\n\n"
        "Let's help each other! 😺"
    )
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=help_text)
    )


def show_profile(reply_token, user):
    """Show user profile with level and experience."""
    next_level_exp = user.level * 100
    exp_percentage = int((user.exp / next_level_exp) * 100) if next_level_exp > 0 else 0
    
    profile_text = (
        f"😺 {user.display_name}'s Profile 😺\n\n"
        f"Level: {user.level}\n"
        f"EXP: {user.exp}/{next_level_exp} ({exp_percentage}%)\n"
        f"Tasks Completed: {user.completed_tasks}\n\n"
        f"Keep helping others to level up! 🌟"
    )
    
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=profile_text)
    )


def show_available_tasks(reply_token):
    """Show list of available tasks."""
    tasks = Task.objects.filter(
        status=Task.TaskStatus.OPEN,
        time__gte=timezone.now()
    ).order_by('time')[:5]  # Limit to 5 tasks
    
    if not tasks:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="No tasks available right now. Check back later or post your own task!")
        )
        return
    
    # Create a buttons template for each task
    messages = []
    
    for task in tasks:
        template = ButtonsTemplate(
            title=task.title[:40],  # LINE limits title to 40 chars
            text=f"{task.description[:60]}... ({task.reward} EXP)",  # LINE limits text
            actions=[
                PostbackAction(
                    label="View Details",
                    data=json.dumps({"action": "detail", "task_id": task.id})
                ),
                PostbackAction(
                    label="Take This Task",
                    data=json.dumps({"action": "take", "task_id": task.id})
                )
            ]
        )
        
        messages.append(TemplateSendMessage(
            alt_text=f"Task: {task.title}",
            template=template
        ))
    
    # Send the first message as a reply, then push the rest
    line_bot_api.reply_message(reply_token, messages[0])
    
    user_id = line_bot_api.get_profile(reply_token).user_id
    for message in messages[1:]:
        line_bot_api.push_message(user_id, message)


def show_user_tasks(reply_token, user):
    """Show tasks posted or taken by the user."""
    posted_tasks = Task.objects.filter(poster=user).order_by('-created_at')[:3]
    taken_tasks = Task.objects.filter(taker=user).order_by('-updated_at')[:3]
    
    if not posted_tasks and not taken_tasks:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="You haven't posted or taken any tasks yet.")
        )
        return
    
    messages = []
    
    # Add posted tasks
    if posted_tasks:
        posted_text = "📤 Your Posted Tasks:\n\n"
        for task in posted_tasks:
            status_emoji = "🆕" if task.status == Task.TaskStatus.OPEN else "🔄" if task.status == Task.TaskStatus.TAKEN else "✅"
            posted_text += f"{status_emoji} {task.title}\n"
        
        messages.append(TextSendMessage(text=posted_text))
    
    # Add taken tasks
    if taken_tasks:
        taken_text = "📥 Your Taken Tasks:\n\n"
        for task in taken_tasks:
            status_emoji = "🔄" if task.status == Task.TaskStatus.TAKEN else "✅"
            taken_text += f"{status_emoji} {task.title}\n"
            
            # Add complete button for taken tasks that aren't done
            if task.status == Task.TaskStatus.TAKEN:
                template = ButtonsTemplate(
                    title=task.title[:40],
                    text=f"Taken task: {task.description[:60]}...",
                    actions=[
                        PostbackAction(
                            label="Mark as Complete",
                            data=json.dumps({"action": "complete", "task_id": task.id})
                        )
                    ]
                )
                messages.append(TemplateSendMessage(
                    alt_text=f"Task: {task.title}",
                    template=template
                ))
        
        messages.append(TextSendMessage(text=taken_text))
    
    # Send the first message as a reply, then push the rest
    line_bot_api.reply_message(reply_token, messages[0])
    
    user_id = user.line_id
    for message in messages[1:]:
        line_bot_api.push_message(user_id, message)


def handle_post_command(reply_token, user, title):
    """Handle the start of task posting process."""
    if not title:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="Please provide a title for your task. Example: post: Buy groceries")
        )
        return
    
    # In a real application, this would start a conversation flow to gather all task details
    # For this demonstration, we'll just acknowledge and provide next steps
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(
            text=f"Starting to create task: '{title}'\n\n"
                 f"In the full app, we would now ask for:\n"
                 f"- Description\n"
                 f"- Location\n"
                 f"- Time\n"
                 f"- Reward points\n\n"
                 f"For now, please use the web interface to complete task creation."
        )
    )


def handle_take_task(reply_token, user, task_id):
    """Handle a user taking a task."""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="Task not found.")
        )
        return
    
    # Check if user is the poster
    if user == task.poster:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="You cannot take your own task.")
        )
        return
    
    # Try to take the task
    success = task.take(user)
    
    if success:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(
                text=f"You've taken the task: {task.title}\n\n"
                     f"Complete it before {task.time.strftime('%Y-%m-%d %H:%M')} to earn {task.reward} EXP!"
            )
        )
        
        # Notify the poster
        try:
            line_bot_api.push_message(
                task.poster.line_id,
                TextSendMessage(
                    text=f"Good news! {user.display_name} has taken your task: {task.title}"
                )
            )
        except LineBotApiError:
            logger.error(f"Failed to notify poster {task.poster.line_id}")
    else:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="Sorry, this task is no longer available.")
        )


def handle_complete_task(reply_token, user, task_id):
    """Handle a user marking a task as complete."""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="Task not found.")
        )
        return
    
    # Check if user is the taker
    if user != task.taker:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="You can only complete tasks you've taken.")
        )
        return
    
    # Try to complete the task
    success = task.complete()
    
    if success:
        # Check if user leveled up
        did_level_up = (user.exp + task.reward) >= (user.level * 100)
        
        if did_level_up:
            message = (
                f"🎉 Task completed: {task.title}\n\n"
                f"You earned {task.reward} EXP and LEVELED UP to level {user.level}! 🌟"
            )
        else:
            message = (
                f"✅ Task completed: {task.title}\n\n"
                f"You earned {task.reward} EXP!"
            )
        
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=message)
        )
        
        # Notify the poster
        try:
            line_bot_api.push_message(
                task.poster.line_id,
                TextSendMessage(
                    text=f"🎉 {user.display_name} has completed your task: {task.title}\n\n"
                         f"Would you like to send a thank you message?"
                )
            )
        except LineBotApiError:
            logger.error(f"Failed to notify poster {task.poster.line_id}")
    else:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="Sorry, there was an issue completing this task.")
        )


def show_task_detail(reply_token, task_id):
    """Show detailed information about a task."""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="Task not found.")
        )
        return
    
    detail_text = (
        f"📋 Task: {task.title}\n\n"
        f"Description: {task.description}\n\n"
        f"📍 Location: {task.location}\n"
        f"⏰ Time: {task.time.strftime('%Y-%m-%d %H:%M')}\n"
        f"💰 Reward: {task.reward} EXP\n\n"
        f"Posted by: {task.poster.display_name}"
    )
    
    if task.status == Task.TaskStatus.OPEN:
        template = ButtonsTemplate(
            title=task.title[:40],
            text=detail_text[:160],  # LINE limits text length
            actions=[
                PostbackAction(
                    label="Take This Task",
                    data=json.dumps({"action": "take", "task_id": task.id})
                )
            ]
        )
        
        line_bot_api.reply_message(
            reply_token,
            TemplateSendMessage(
                alt_text=f"Task: {task.title}",
                template=template
            )
        )
    else:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=detail_text)
        )