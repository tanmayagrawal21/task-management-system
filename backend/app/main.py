from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import auth, tasks, users

tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication. Use `/auth/login` to obtain a JWT token, then click **Authorize** above to use it across all endpoints.",
    },
    {
        "name": "tasks",
        "description": "Create, read, update, and soft-delete tasks. All endpoints require authentication.",
    },
    {
        "name": "users",
        "description": "Retrieve users for task assignment. All endpoints require authentication.",
    },
]

app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description=(
        "REST API for the Task Management System.\n\n"
        "**Getting started:** call `POST /auth/login` with your credentials, "
        "then click the **Authorize** button and paste the returned `access_token`."
    ),
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/health", tags=["health"], summary="Health check", include_in_schema=False)
def health_check():
    return {"status": "ok"}
