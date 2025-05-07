# MeowTask (喵一下) - A LINE-based Task Matching Service

MeowTask is a lightweight mission matching service built on Django 4.2 with LINE integration. Users can post small daily tasks, accept tasks from others, and earn experience points to level up.

## 🌟 Features

- LINE login integration
- Post and manage daily tasks
- Find and accept tasks near you
- Complete tasks to earn EXP and level up
- Send thank-you messages for completed tasks
- RESTful API for all functionality
- LINE bot for notifications and quick actions

## 🧱 Project Structure

- `meowtask/`: Core Django settings
- `users/`: User model and authentication
- `tasks/`: Task management
- `linebot/`: LINE Messaging API integration

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- LINE developer account

### Installation

1. Clone the repository
2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`

5. Run migrations

```bash
python manage.py migrate
```

6. Create a superuser

```bash
python manage.py createsuperuser
```

7. Run the development server

```bash
python manage.py runserver
```

## 🧪 API Endpoints

### Users

- `GET /api/users/profile/`: Get current user profile
- `GET /api/users/profile/<line_id>/`: Get user by LINE ID
- `GET /api/users/leaderboard/`: Get user leaderboard

### Tasks

- `GET /api/tasks/`: List available tasks
- `POST /api/tasks/`: Create a new task
- `GET /api/tasks/<id>/`: Get task details
- `POST /api/tasks/<id>/take/`: Take a task
- `POST /api/tasks/<id>/complete/`: Complete a task
- `GET /api/tasks/my-tasks/`: List user's tasks
- `GET /api/tasks/nearby/?location=<location>`: Find nearby tasks
- `POST /api/tasks/thanks/`: Send a thanks message

### LINE Webhook

- `POST /webhook/line/`: Webhook for LINE events

## 🔧 Configuration

The project uses environment variables for configuration. Create a `.env` file with:

```
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key

# Database settings
DB_NAME=meowtask_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Line Bot settings
LINE_CHANNEL_SECRET=your-line-channel-secret
LINE_CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
```

## 🌐 LINE Bot Commands

- `help`: Show available commands
- `profile`: Show user profile
- `tasks`: List available tasks
- `my tasks`: Show tasks posted or taken by user
- `post: [title]`: Start posting a new task

## 🛡️ License

This project is licensed under the MIT License - see the LICENSE file for details.