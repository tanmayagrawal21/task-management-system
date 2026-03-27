from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.task import PaginatedTasks, TaskCreate, TaskOut, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "",
    response_model=PaginatedTasks,
    summary="List tasks",
    description=(
        "Returns a paginated list of tasks. Optionally filter by `status` and/or `assigned_user_id`. "
        "Results are ordered by creation date descending. Deleted tasks are never returned."
    ),
    responses={
        401: {"description": "Missing or invalid token"},
    },
)
def list_tasks(
    page: int = Query(1, ge=1, description="Page number, starting at 1."),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page (max 100)."),
    status: TaskStatus | None = Query(None, description="Filter by task status."),
    assigned_user_id: int | None = Query(None, description="Filter by assigned user ID."),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return task_service.get_tasks(db, page, page_size, status, assigned_user_id)


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Creates a new task. `title` is required. `status` defaults to `Todo` if not provided.",
    responses={
        401: {"description": "Missing or invalid token"},
        422: {"description": "Validation error — title is empty or assigned user does not exist"},
    },
)
def create_task(data: TaskCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return task_service.create_task(data, db)


@router.put(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update task",
    description="Partially updates a task. Only fields included in the request body are changed.",
    responses={
        401: {"description": "Missing or invalid token"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error — title is empty or assigned user does not exist"},
    },
)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return task_service.update_task(task_id, data, db)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Soft-deletes a task by setting its `deleted_at` timestamp. The task is no longer returned in any listing.",
    responses={
        401: {"description": "Missing or invalid token"},
        404: {"description": "Task not found"},
    },
)
def delete_task(task_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    task_service.delete_task(task_id, db)
