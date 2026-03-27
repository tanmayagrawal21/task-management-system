from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserOut],
    summary="List users",
    description="Returns all active users, ordered by name. Used to populate the assignee dropdown when creating or editing tasks.",
    responses={
        401: {"description": "Missing or invalid token"},
    },
)
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return user_service.list_users(db)
