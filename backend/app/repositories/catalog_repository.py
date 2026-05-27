from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import CategoryModel, ProductModel
from app.domain.catalog import Category, Product


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, category: Category) -> Category:
        model = CategoryModel.from_domain(category)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def get_by_name(self, name: str) -> Category | None:
        statement = select(CategoryModel).where(CategoryModel.name == name)
        model = self.db.scalar(statement)
        return model.to_domain() if model else None

    def get_by_id(self, category_id: UUID) -> Category | None:
        model = self.db.get(CategoryModel, str(category_id))
        return model.to_domain() if model else None

    def list_all(self) -> list[Category]:
        statement = select(CategoryModel).order_by(CategoryModel.name.asc())
        return [model.to_domain() for model in self.db.scalars(statement)]


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, product: Product) -> Product:
        model = ProductModel.from_domain(product)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def list_all(
        self,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> list[Product]:
        statement = select(ProductModel).order_by(ProductModel.name.asc())
        if not include_inactive:
            statement = statement.where(ProductModel.is_active.is_(True))
        if search:
            statement = statement.where(ProductModel.name.ilike(f"%{search}%"))
        return [model.to_domain() for model in self.db.scalars(statement)]

    def get_by_id(self, product_id: UUID) -> Product | None:
        model = self.db.get(ProductModel, str(product_id))
        return model.to_domain() if model else None

    def get_by_ids(self, product_ids: list[UUID]) -> list[Product]:
        ids = [str(product_id) for product_id in product_ids]
        statement = select(ProductModel).where(ProductModel.id.in_(ids))
        return [model.to_domain() for model in self.db.scalars(statement)]

    def update(self, product: Product) -> Product:
        model = self.db.get(ProductModel, str(product.id))
        if model is None:
            msg = "Product was not found."
            raise LookupError(msg)

        model.category_id = str(product.category_id)
        model.name = product.name
        model.price = product.price
        model.emoji = product.emoji
        model.image_path = product.image_path
        model.is_active = product.is_active
        model.created_at = product.created_at
        model.updated_at = product.updated_at
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()
