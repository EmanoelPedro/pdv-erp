from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.shared import ensure_utc, normalize_money, utc_now


@dataclass(frozen=True, slots=True)
class Category:
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        name: str,
        created_at: datetime | None = None,
    ) -> "Category":
        occurred_at = ensure_utc(created_at or utc_now())
        return cls(
            id=uuid4(),
            name=name,
            is_active=True,
            created_at=occurred_at,
            updated_at=occurred_at,
        )


@dataclass(frozen=True, slots=True)
class Product:
    id: UUID
    category_id: UUID
    name: str
    price: Decimal
    emoji: str | None
    image_path: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        category_id: UUID,
        name: str,
        price: Decimal,
        emoji: str | None = None,
        image_path: str | None = None,
        created_at: datetime | None = None,
    ) -> "Product":
        occurred_at = ensure_utc(created_at or utc_now())
        return cls(
            id=uuid4(),
            category_id=category_id,
            name=name,
            price=normalize_money(price),
            emoji=emoji.strip() or None if emoji else None,
            image_path=image_path,
            is_active=True,
            created_at=occurred_at,
            updated_at=occurred_at,
        )
