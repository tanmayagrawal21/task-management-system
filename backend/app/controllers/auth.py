from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description=(
        "Authenticate with email and password. Returns a JWT bearer token valid for 8 hours. "
        "Use the token in the `Authorization: Bearer <token>` header for all protected endpoints."
    ),
    responses={
        401: {"description": "Invalid email or password"},
    },
)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login(email=form.username, password=form.password, db=db)
