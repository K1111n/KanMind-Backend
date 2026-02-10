# KanMind Backend

A Django REST Framework backend for a Kanban board application. Provides user authentication, board management, task tracking, and commenting functionality.

## Tech Stack

- Python 3
- Django 4.2
- Django REST Framework 3.14
- Token Authentication
- SQLite (development)

## Setup

```bash
# Clone the repository
git clone <repository-url>
cd KanMind-Backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo 'SECRET_KEY=your-secret-key-here' > .env
echo 'DEBUG=True' >> .env

# Run migrations
python3 manage.py migrate

# Create a superuser (optional)
python3 manage.py createsuperuser

# Start the development server
python3 manage.py runserver
```

## API Endpoints

### Authentication

| Method | Endpoint              | Description                |
|--------|-----------------------|----------------------------|
| POST   | `/api/registration/`  | Register a new user        |
| POST   | `/api/login/`         | Log in and receive a token |
| GET    | `/api/email-check/`   | Check if email exists      |

### Boards

| Method | Endpoint               | Description             |
|--------|------------------------|-------------------------|
| GET    | `/api/boards/`         | List boards for user    |
| POST   | `/api/boards/`         | Create a new board      |
| GET    | `/api/boards/{id}/`    | Board detail with tasks |
| PATCH  | `/api/boards/{id}/`    | Update board            |
| DELETE | `/api/boards/{id}/`    | Delete board            |

### Tasks

| Method | Endpoint                                  | Description                    |
|--------|-------------------------------------------|--------------------------------|
| GET    | `/api/tasks/assigned-to-me/`              | Tasks assigned to current user |
| GET    | `/api/tasks/reviewing/`                   | Tasks where user is reviewer   |
| POST   | `/api/tasks/`                             | Create a new task              |
| PATCH  | `/api/tasks/{id}/`                        | Update a task                  |
| DELETE | `/api/tasks/{id}/`                        | Delete a task                  |
| GET    | `/api/tasks/{id}/comments/`               | List comments on a task        |
| POST   | `/api/tasks/{id}/comments/`               | Add a comment to a task        |
| DELETE | `/api/tasks/{id}/comments/{comment_id}/`  | Delete a comment               |

## Testing

```bash
# Run all tests
python3 manage.py test

# Run tests for a specific app
python3 manage.py test auth_app
python3 manage.py test board_app
python3 manage.py test tasks_app

# Run with verbosity
python3 manage.py test -v2
```

## Project Structure

```
KanMind-Backend/
    core/               # Project settings and root URL config
    auth_app/           # Registration, login, email check
        api/
    board_app/          # Board CRUD
        api/
    tasks_app/          # Task and comment management
        api/
    manage.py
    requirements.txt
    .env                # Environment variables (not in repo)
```
