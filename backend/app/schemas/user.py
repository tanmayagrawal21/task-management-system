from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserOut(BaseModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Alice Martin"])
    email: EmailStr = Field(examples=["alice@example.com"])
    created_at: datetime = Field(examples=["2024-01-15T09:00:00"])

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Jane Doe"])
    email: EmailStr = Field(examples=["jane@example.com"])
    password: str = Field(min_length=8, examples=["supersecret"])

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="JWT bearer token. Include as `Authorization: Bearer <token>` on subsequent requests.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(default="bearer", examples=["bearer"])
    user: UserOut
