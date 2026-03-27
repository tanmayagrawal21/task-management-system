"""Seed the database with sample users and tasks."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.user import User
from app.models.task import Task, TaskStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = [
    {"name": "Alice Martin", "email": "alice@example.com", "password": "password123"},
    {"name": "Bob Chen", "email": "bob@example.com", "password": "password123"},
    {"name": "Carol Davis", "email": "carol@example.com", "password": "password123"},
]

TASKS = [
    {
        "title": "Design database schema",
        "description": "Create ERD and finalize table definitions for the project.",
        "status": TaskStatus.done,
        "assigned_to": 0,   # Alice
        "created_by": 0,    # Alice
    },
    {
        "title": "Set up CI/CD pipeline",
        "description": "Configure GitHub Actions for automated testing and deployment.",
        "status": TaskStatus.in_progress,
        "assigned_to": 1,   # Bob
        "created_by": 0,    # Alice
    },
    {
        "title": "Implement authentication",
        "description": "Add JWT-based login and protected routes to the API.",
        "status": TaskStatus.done,
        "assigned_to": 0,   # Alice
        "created_by": 1,    # Bob
    },
    {
        "title": "Build task list UI",
        "description": "Create the main task list view with pagination and filters.",
        "status": TaskStatus.in_progress,
        "assigned_to": 2,   # Carol
        "created_by": 1,    # Bob
    },
    {
        "title": "Write API documentation",
        "description": "Document all endpoints with request/response examples.",
        "status": TaskStatus.todo,
        "assigned_to": 1,   # Bob
        "created_by": 2,    # Carol
    },
    {
        "title": "Add unit tests for services",
        "description": "Cover task and auth service logic with pytest tests.",
        "status": TaskStatus.todo,
        "assigned_to": 0,   # Alice
        "created_by": 2,    # Carol
    },
    {
        "title": "Mobile responsive layout",
        "description": "Ensure the UI works correctly on small screens.",
        "status": TaskStatus.todo,
        "assigned_to": 2,   # Carol
        "created_by": 0,    # Alice
    },
    {
        "title": "Integrate AI assistant",
        "description": "Add optional LLM chat panel supporting Claude, OpenAI, and Gemini.",
        "status": TaskStatus.todo,
        "assigned_to": 1,   # Bob
        "created_by": 1,    # Bob
    },
    {
        "title": "Performance review",
        "description": "Profile slow queries and add missing indexes.",
        "status": TaskStatus.todo,
        "assigned_to": None,
        "created_by": 2,    # Carol
    },
    {
        "title": "Stakeholder demo preparation",
        "description": "Prepare demo script and seed data for the client walkthrough.",
        "status": TaskStatus.in_progress,
        "assigned_to": 2,   # Carol
        "created_by": 0,    # Alice
    },
]


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        users = []
        for u in USERS:
            user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=pwd_context.hash(u["password"]),
            )
            db.add(user)
            users.append(user)

        db.flush()

        for t in TASKS:
            assigned_id = users[t["assigned_to"]].id if t["assigned_to"] is not None else None
            task = Task(
                title=t["title"],
                description=t["description"],
                status=t["status"],
                assigned_user_id=assigned_id,
                created_by_id=users[t["created_by"]].id,
            )
            db.add(task)

        db.commit()
        print(f"Seeded {len(users)} users and {len(TASKS)} tasks.")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
