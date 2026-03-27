from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.task import TaskStatus
from app.schemas.user import UserOut


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255, examples=["Fix login bug"])
    description: str | None = Field(default=None, examples=["Users are unable to log in with valid credentials."])
    status: TaskStatus = Field(default=TaskStatus.todo, examples=[TaskStatus.todo])
    assigned_user_id: int | None = Field(default=None, examples=[1])

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255, examples=["Fix login bug (updated)"])
    description: str | None = Field(default=None, examples=["Updated description."])
    status: TaskStatus | None = Field(default=None, examples=[TaskStatus.in_progress])
    assigned_user_id: int | None = Field(default=None, examples=[2])

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class TaskOut(BaseModel):
    id: int = Field(examples=[1])
    title: str = Field(examples=["Fix login bug"])
    description: str | None = Field(examples=["Users are unable to log in with valid credentials."])
    status: TaskStatus = Field(examples=[TaskStatus.in_progress])
    assigned_user_id: int | None = Field(examples=[1])
    assigned_user: UserOut | None
    created_at: datetime = Field(examples=["2024-01-15T09:00:00"])
    updated_at: datetime = Field(examples=["2024-01-16T14:30:00"])

    model_config = {"from_attributes": True}


class PaginatedTasks(BaseModel):
    items: list[TaskOut]
    total: int = Field(description="Total number of tasks matching the current filters.", examples=[42])
    page: int = Field(description="Current page number.", examples=[1])
    page_size: int = Field(description="Number of items per page.", examples=[20])
    total_pages: int = Field(description="Total number of pages.", examples=[3])
