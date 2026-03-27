from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import TokenResponse, UserCreate
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


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register",
    description="Create a new account. Returns a JWT token immediately so the user is logged in after registration.",
    responses={
        409: {"description": "An account with this email already exists"},
        422: {"description": "Validation error — name empty, invalid email, or password too short"},
    },
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register(data, db)
