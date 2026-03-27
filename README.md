# Task Management Application

**Live demo:** [tskmgmt.fly.dev](https://tskmgmt.fly.dev) — API docs: [tskmgmt-api.fly.dev/docs](https://tskmgmt-api.fly.dev/docs)

A full-stack task management system with a FastAPI backend and Vue 3 frontend.

> **AI Assistant** — click the ✦ button on the task list to open a chat panel powered by your own LLM API key (Claude, OpenAI, or Gemini). The assistant has full context of the task list and can answer questions, summarize progress, and perform actions like creating or updating tasks on your behalf. API keys and conversation history are stored in your browser only. Tested with Claude and Gemini — OpenAI support is not guaranteed.

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

### Option A — Docker (recommended)

Requires [Docker](https://docs.docker.com/get-docker/) and Docker Compose.

```bash
# Set a secret key for JWT signing (required)
export SECRET_KEY=your-secret-key-here

docker compose up --build
```

The app will be available at <http://localhost:8080>.

API docs at <http://localhost:8000/docs>

> The database is stored in a Docker volume (`db_data`) and persists across restarts.
> To load sample data, run `docker compose exec backend python seed.py`.

---

### Option B — Manual setup

#### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set a SECRET_KEY

alembic upgrade head            # create database tables
python seed.py                  # load sample data (optional)

uvicorn app.main:app --reload
```

Backend runs at <http://localhost:8000>

API docs at <http://localhost:8000/docs>

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at <http://localhost:5173>

---

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
