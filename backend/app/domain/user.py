from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.shared import ensure_utc, utc_now


class UserRole(StrEnum):
    OWNER = "OWNER"
    EMPLOYEE = "EMPLOYEE"


@dataclass(frozen=True, slots=True)
class User:
    id: UUID
    full_name: str
    username: str
    role: UserRole
    pin_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        full_name: str,
        username: str,
        role: UserRole,
        pin_hash: str,
        created_at: datetime | None = None,
    ) -> "User":
        occurred_at = ensure_utc(created_at or utc_now())
        return cls(
            id=uuid4(),
            full_name=full_name,
            username=username,
            role=role,
            pin_hash=pin_hash,
            is_active=True,
            created_at=occurred_at,
            updated_at=occurred_at,
        )


@dataclass(frozen=True, slots=True)
class UserSession:
    id: UUID
    user_id: UUID
    token_hash: str
    created_at: datetime
    expires_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UUID,
        token_hash: str,
        created_at: datetime,
        expires_at: datetime,
    ) -> "UserSession":
        return cls(
            id=uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            created_at=ensure_utc(created_at),
            expires_at=ensure_utc(expires_at),
        )
