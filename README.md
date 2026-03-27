# Task Management Application

A full-stack task management system with a FastAPI backend and Vue 3 frontend.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | Vue 3 + TypeScript + Vite + Tailwind CSS + PrimeVue |
| Backend | Python + FastAPI |
| Database | SQLite + SQLAlchemy + Alembic |
| Auth | JWT (python-jose) |
| API Docs | Swagger UI (built into FastAPI) |

## Project Structure

```text
task_mgmt/
├── backend/
│   ├── app/
│   │   ├── controllers/   Route handlers (HTTP layer)
│   │   ├── services/      Business logic
│   │   ├── models/        SQLAlchemy ORM models
│   │   ├── schemas/       Pydantic request/response schemas
│   │   └── core/          Config, JWT, auth dependencies
│   ├── alembic/           Database migrations
│   ├── seed.py            Sample data script
│   └── requirements.txt
└── frontend/
    └── src/
        ├── views/         Page-level components
        ├── components/    Reusable UI components
        ├── stores/        Pinia state (auth, tasks)
        ├── services/      Axios API client
        └── router/        Vue Router + auth guard
```

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set a SECRET_KEY

alembic upgrade head            # create database tables
python seed.py                  # load sample data

uvicorn app.main:app --reload
```

Backend runs at <http://localhost:8000>

API docs at <http://localhost:8000/docs>

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at <http://localhost:5173>

## API Overview

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | No | Create account, returns JWT |
| POST | `/auth/login` | No | Login, returns JWT |
| GET | `/users` | Yes | List all users |
| GET | `/tasks` | Yes | List tasks (paginated, filterable) |
| POST | `/tasks` | Yes | Create a task |
| PUT | `/tasks/{id}` | Yes | Update a task |
| POST | `/tasks/{id}/claim` | Yes | Assign yourself to an unassigned task |
| DELETE | `/tasks/{id}` | Yes | Soft-delete a task |

### Query parameters for `GET /tasks`

| Param | Type | Description |
| --- | --- | --- |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (default: 20, max: 100) |
| `status` | string | Filter by `Todo`, `In Progress`, or `Done` |
| `assigned_user_id` | int | Filter by assigned user |

Full interactive documentation is available at <http://localhost:8000/docs> when the backend is running.

## Permissions

| Action | Who |
| --- | --- |
| View all tasks | Any authenticated user |
| Create task | Any authenticated user (becomes creator) |
| Edit task | Creator or current assignee |
| Claim unassigned task | Any authenticated user |
| Delete task | Creator only |

## Accounts

Register directly from the login page — no invite needed.

For local development, `backend/seed.py` populates the database with sample users and tasks. Run it once after the migration step. Credentials are defined in that file.

## Database

SQLite with SQLAlchemy ORM. Schema managed via Alembic migrations.

- `users` — id, name, email, hashed_password, created_at, deleted_at
- `tasks` — id, title, description, status, assigned_user_id (FK), created_by_id (FK), created_at, updated_at, deleted_at

Tasks support soft delete (`deleted_at` timestamp). Indexes on `status`, `assigned_user_id`, and `created_by_id` for query performance.
