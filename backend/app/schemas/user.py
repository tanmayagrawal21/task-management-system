from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Alice Martin"])
    email: EmailStr = Field(examples=["alice@example.com"])
    created_at: datetime = Field(examples=["2024-01-15T09:00:00"])

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="JWT bearer token. Include as `Authorization: Bearer <token>` on subsequent requests.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(default="bearer", examples=["bearer"])
    user: UserOut
