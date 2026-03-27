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
    responses={401: {"description": "Missing or invalid token"}},
)
def list_tasks(
    page: int = Query(1, ge=1, description="Page number, starting at 1."),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page (max 100)."),
    status_filter: TaskStatus | None = Query(None, alias="status", description="Filter by task status."),
    assigned_user_id: int | None = Query(None, description="Filter by assigned user ID."),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return task_service.get_tasks(db, page, page_size, status_filter, assigned_user_id)


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Creates a new task. The authenticated user becomes the creator. `title` is required. `status` defaults to `Todo`.",
    responses={
        401: {"description": "Missing or invalid token"},
        422: {"description": "Validation error — title is empty or assigned user does not exist"},
    },
)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.create_task(data, current_user, db)


@router.put(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update task",
    description="Partially updates a task. Only the task creator or the assigned user can edit. Only fields included in the request body are changed.",
    responses={
        401: {"description": "Missing or invalid token"},
        403: {"description": "Not the creator or assignee"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error — title is empty or assigned user does not exist"},
    },
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.update_task(task_id, data, current_user, db)


@router.post(
    "/{task_id}/claim",
    response_model=TaskOut,
    summary="Claim task",
    description="Assigns the authenticated user to an unassigned task. Fails if the task already has an assignee.",
    responses={
        401: {"description": "Missing or invalid token"},
        404: {"description": "Task not found"},
        409: {"description": "Task is already assigned"},
    },
)
def claim_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.claim_task(task_id, current_user, db)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Soft-deletes a task. Only the task creator can delete.",
    responses={
        401: {"description": "Missing or invalid token"},
        403: {"description": "Not the task creator"},
        404: {"description": "Task not found"},
    },
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_service.delete_task(task_id, current_user, db)
