from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.catalog import Category, Product

MoneyInput = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]


class CreateCategoryRequest(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=120)]


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, category: Category) -> "CategoryResponse":
        return cls(
            id=category.id,
            name=category.name,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )


class CreateProductRequest(BaseModel):
    category_id: UUID
    name: Annotated[str, Field(min_length=2, max_length=120)]
    price: MoneyInput
    emoji: Annotated[str | None, Field(max_length=16)] = None


class UpdateProductRequest(BaseModel):
    category_id: UUID
    name: Annotated[str, Field(min_length=2, max_length=120)]
    price: MoneyInput
    emoji: Annotated[str | None, Field(max_length=16)] = None
    remove_image: bool = False


class ProductResponse(BaseModel):
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
    def from_domain(cls, product: Product) -> "ProductResponse":
        return cls(
            id=product.id,
            category_id=product.category_id,
            name=product.name,
            price=product.price,
            emoji=product.emoji,
            image_path=product.image_path,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
