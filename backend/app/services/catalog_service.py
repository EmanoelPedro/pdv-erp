from dataclasses import replace
from decimal import Decimal
from uuid import UUID

from app.domain.catalog import Category, Product
from app.domain.exceptions import CategoryNotFoundError, DuplicateCategoryNameError, ProductNotFoundError
from app.domain.shared import utc_now
from app.domain.user import User
from app.repositories.catalog_repository import CategoryRepository, ProductRepository
from app.services.auth_service import AuthService


class CatalogService:
    def __init__(
        self,
        category_repository: CategoryRepository,
        product_repository: ProductRepository,
        auth_service: AuthService,
    ) -> None:
        self.category_repository = category_repository
        self.product_repository = product_repository
        self.auth_service = auth_service

    def list_categories(self) -> list[Category]:
        return self.category_repository.list_all()

    def create_category(self, name: str, actor: User) -> Category:
        self.auth_service.require_owner(actor)
        normalized_name = name.strip()
        if self.category_repository.get_by_name(normalized_name) is not None:
            raise DuplicateCategoryNameError("This category already exists.")

        category = Category.create(name=normalized_name)
        try:
            created_category = self.category_repository.create(category)
            self.category_repository.db.commit()
            return created_category
        except Exception:
            self.category_repository.db.rollback()
            raise

    def list_products(self, search: str | None = None) -> list[Product]:
        return self.product_repository.list_all(search=search)

    def list_all_products(
        self,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> list[Product]:
        return self.product_repository.list_all(
            search=search,
            include_inactive=include_inactive,
        )

    def create_product(
        self,
        category_id: UUID,
        name: str,
        price: Decimal,
        emoji: str | None,
        actor: User,
    ) -> Product:
        self.auth_service.require_owner(actor)
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError("Category was not found.")

        product = Product.create(
            category_id=category.id,
            name=name.strip(),
            price=price,
            emoji=emoji,
        )
        try:
            created_product = self.product_repository.create(product)
            self.product_repository.db.commit()
            return created_product
        except Exception:
            self.product_repository.db.rollback()
            raise

    def update_product_image(
        self,
        product_id: UUID,
        image_path: str,
        actor: User,
    ) -> Product:
        self.auth_service.require_owner(actor)
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product was not found.")

        updated_product = replace(
            product,
            image_path=image_path,
            updated_at=utc_now(),
        )
        try:
            persisted_product = self.product_repository.update(updated_product)
            self.product_repository.db.commit()
            return persisted_product
        except Exception:
            self.product_repository.db.rollback()
            raise

    def update_product(
        self,
        product_id: UUID,
        category_id: UUID,
        name: str,
        price: Decimal,
        emoji: str | None,
        remove_image: bool,
        actor: User,
    ) -> Product:
        self.auth_service.require_owner(actor)
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product was not found.")

        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError("Category was not found.")

        updated_product = replace(
            product,
            category_id=category.id,
            name=name.strip(),
            price=price,
            emoji=emoji.strip() or None if emoji else None,
            image_path=None if remove_image else product.image_path,
            updated_at=utc_now(),
        )
        try:
            persisted_product = self.product_repository.update(updated_product)
            self.product_repository.db.commit()
            return persisted_product
        except Exception:
            self.product_repository.db.rollback()
            raise

    def deactivate_product(
        self,
        product_id: UUID,
        actor: User,
    ) -> Product:
        self.auth_service.require_owner(actor)
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product was not found.")

        updated_product = replace(
            product,
            is_active=False,
            updated_at=utc_now(),
        )
        try:
            persisted_product = self.product_repository.update(updated_product)
            self.product_repository.db.commit()
            return persisted_product
        except Exception:
            self.product_repository.db.rollback()
            raise

    def restore_product(
        self,
        product_id: UUID,
        actor: User,
    ) -> Product:
        self.auth_service.require_owner(actor)
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product was not found.")

        updated_product = replace(
            product,
            is_active=True,
            updated_at=utc_now(),
        )
        try:
            persisted_product = self.product_repository.update(updated_product)
            self.product_repository.db.commit()
            return persisted_product
        except Exception:
            self.product_repository.db.rollback()
            raise
