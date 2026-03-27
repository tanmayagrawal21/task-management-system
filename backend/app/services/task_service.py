from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import PaginatedTasks, TaskCreate, TaskOut, TaskUpdate


def _base_query(db: Session):
    return (
        db.query(Task)
        .options(joinedload(Task.assigned_user), joinedload(Task.created_by))
        .filter(Task.deleted_at.is_(None))
    )


def _validate_user(user_id: int | None, db: Session) -> None:
    if user_id is not None:
        exists = db.query(User.id).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        if not exists:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Assigned user not found")


def _check_can_edit(task: Task, current_user: User) -> None:
    if task.created_by_id == current_user.id:
        return
    if task.assigned_user_id == current_user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the task creator or assignee can edit this task")


def _check_can_delete(task: Task, current_user: User) -> None:
    if task.created_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the task creator can delete this task")


def get_tasks(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status_filter: TaskStatus | None = None,
    assigned_user_id: int | None = None,
) -> PaginatedTasks:
    query = _base_query(db)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter)
    if assigned_user_id is not None:
        query = query.filter(Task.assigned_user_id == assigned_user_id)

    total = query.count()
    items = query.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedTasks(
        items=[TaskOut.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, -(-total // page_size)),
    )


def create_task(data: TaskCreate, current_user: User, db: Session) -> TaskOut:
    _validate_user(data.assigned_user_id, db)
    task = Task(**data.model_dump(), created_by_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(_base_query(db).filter(Task.id == task.id).one())


def update_task(task_id: int, data: TaskUpdate, current_user: User, db: Session) -> TaskOut:
    task = _base_query(db).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    _check_can_edit(task, current_user)

    updates = data.model_dump(exclude_unset=True)
    if "assigned_user_id" in updates:
        _validate_user(updates["assigned_user_id"], db)

    for field, value in updates.items():
        setattr(task, field, value)

    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(_base_query(db).filter(Task.id == task_id).one())


def claim_task(task_id: int, current_user: User, db: Session) -> TaskOut:
    task = _base_query(db).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.assigned_user_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task is already assigned")

    task.assigned_user_id = current_user.id
    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(_base_query(db).filter(Task.id == task_id).one())


def delete_task(task_id: int, current_user: User, db: Session) -> None:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    _check_can_delete(task, current_user)

    task.deleted_at = datetime.now(timezone.utc)
    db.commit()
