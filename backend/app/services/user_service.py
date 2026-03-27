from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserOut


def list_users(db: Session) -> list[UserOut]:
    users = db.query(User).filter(User.deleted_at.is_(None)).order_by(User.name).all()
    return [UserOut.model_validate(u) for u in users]
