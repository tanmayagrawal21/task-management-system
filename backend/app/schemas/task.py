from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.task import TaskStatus
from app.schemas.user import UserOut


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    assigned_user_id: int | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    assigned_user_id: int | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    assigned_user_id: int | None
    assigned_user: UserOut | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTasks(BaseModel):
    items: list[TaskOut]
    total: int
    page: int
    page_size: int
    total_pages: int
