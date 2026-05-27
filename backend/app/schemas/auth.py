from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.user import User, UserRole

PinInput = Annotated[str, Field(
    min_length=4, max_length=12, pattern=r"^[0-9]+$")]


class RegisterUserRequest(BaseModel):
    full_name: Annotated[str, Field(min_length=2, max_length=120)]
    username: Annotated[str, Field(
        min_length=3, max_length=60, pattern=r"^[a-zA-Z0-9_.-]+$")]
    pin: PinInput
    role: UserRole | None = None


class LoginRequest(BaseModel):
    username: str
    pin: PinInput


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            full_name=user.full_name,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class SetupStateResponse(BaseModel):
    has_users: bool
