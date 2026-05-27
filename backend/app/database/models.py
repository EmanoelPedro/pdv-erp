from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.domain.cash_register import CashRegisterSession, CashRegisterStatus
from app.domain.catalog import Category, Product
from app.domain.expense import Expense, ExpenseCategory
from app.domain.sale import PaymentMethod, Sale, SaleItem, SaleStatus
from app.domain.sync_queue import SyncQueueEntry, SyncStatus
from app.domain.user import User, UserRole, UserSession


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


class CashRegisterSessionModel(Base):
    __tablename__ = "cash_register_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    opening_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    closing_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True)
    difference_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, session: CashRegisterSession) -> "CashRegisterSessionModel":
        return cls(
            id=str(session.id),
            status=session.status.value,
            opening_amount=session.opening_amount,
            expected_amount=session.expected_amount,
            closing_amount=session.closing_amount,
            difference_amount=session.difference_amount,
            opened_at=session.opened_at,
            closed_at=session.closed_at,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    def update_from_domain(self, session: CashRegisterSession) -> None:
        self.status = session.status.value
        self.opening_amount = session.opening_amount
        self.expected_amount = session.expected_amount
        self.closing_amount = session.closing_amount
        self.difference_amount = session.difference_amount
        self.opened_at = session.opened_at
        self.closed_at = session.closed_at
        self.created_at = session.created_at
        self.updated_at = session.updated_at

    def to_domain(self) -> CashRegisterSession:
        return CashRegisterSession(
            id=UUID(self.id),
            status=CashRegisterStatus(self.status),
            opening_amount=self.opening_amount,
            expected_amount=self.expected_amount,
            closing_amount=self.closing_amount,
            difference_amount=self.difference_amount,
            opened_at=_as_utc(self.opened_at),
            closed_at=_as_utc(self.closed_at),
            created_at=_as_utc(self.created_at),
            updated_at=_as_utc(self.updated_at),
        )


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    username: Mapped[str] = mapped_column(
        String(60), nullable=False, unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    pin_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=str(user.id),
            full_name=user.full_name,
            username=user.username,
            role=user.role.value,
            pin_hash=user.pin_hash,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def to_domain(self) -> User:
        return User(
            id=UUID(self.id),
            full_name=self.full_name,
            username=self.username,
            role=UserRole(self.role),
            pin_hash=self.pin_hash,
            is_active=self.is_active,
            created_at=_as_utc(self.created_at),
            updated_at=_as_utc(self.updated_at),
        )


class UserSessionModel(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, session: UserSession) -> "UserSessionModel":
        return cls(
            id=str(session.id),
            user_id=str(session.user_id),
            token_hash=session.token_hash,
            created_at=session.created_at,
            expires_at=session.expires_at,
        )

    def to_domain(self) -> UserSession:
        return UserSession(
            id=UUID(self.id),
            user_id=UUID(self.user_id),
            token_hash=self.token_hash,
            created_at=_as_utc(self.created_at),
            expires_at=_as_utc(self.expires_at),
        )


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, category: Category) -> "CategoryModel":
        return cls(
            id=str(category.id),
            name=category.name,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

    def to_domain(self) -> Category:
        return Category(
            id=UUID(self.id),
            name=self.name,
            is_active=self.is_active,
            created_at=_as_utc(self.created_at),
            updated_at=_as_utc(self.updated_at),
        )


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    emoji: Mapped[str | None] = mapped_column(String(16), nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, product: Product) -> "ProductModel":
        return cls(
            id=str(product.id),
            category_id=str(product.category_id),
            name=product.name,
            price=product.price,
            emoji=product.emoji,
            image_path=product.image_path,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def to_domain(self) -> Product:
        return Product(
            id=UUID(self.id),
            category_id=UUID(self.category_id),
            name=self.name,
            price=self.price,
            emoji=self.emoji,
            image_path=self.image_path,
            is_active=self.is_active,
            created_at=_as_utc(self.created_at),
            updated_at=_as_utc(self.updated_at),
        )


class SaleModel(Base):
    __tablename__ = "sales"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cash_register_session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cash_register_sessions.id"), nullable=False, index=True)
    seller_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    subtotal_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    cash_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    pix_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    debit_card_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    credit_card_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

    @classmethod
    def from_domain(cls, sale: Sale) -> "SaleModel":
        return cls(
            id=str(sale.id),
            cash_register_session_id=str(sale.cash_register_session_id),
            seller_user_id=str(sale.seller_user_id),
            payment_method=sale.payment_method.value,
            subtotal_amount=sale.subtotal_amount,
            total_amount=sale.total_amount,
            cash_amount=sale.cash_amount,
            pix_amount=sale.pix_amount,
            debit_card_amount=sale.debit_card_amount,
            credit_card_amount=sale.credit_card_amount,
            status=sale.status.value,
            created_at=sale.created_at,
            updated_at=sale.updated_at,
            cancelled_at=sale.cancelled_at,
        )

    def to_domain(self, items: tuple[SaleItem, ...]) -> Sale:
        return Sale(
            id=UUID(self.id),
            cash_register_session_id=UUID(self.cash_register_session_id),
            seller_user_id=UUID(self.seller_user_id),
            payment_method=PaymentMethod(self.payment_method),
            subtotal_amount=self.subtotal_amount,
            total_amount=self.total_amount,
            cash_amount=self.cash_amount,
            pix_amount=self.pix_amount,
            debit_card_amount=self.debit_card_amount,
            credit_card_amount=self.credit_card_amount,
            status=SaleStatus(self.status),
            created_at=_as_utc(self.created_at),
            updated_at=_as_utc(self.updated_at),
            cancelled_at=_as_utc(self.cancelled_at),
            items=items,
        )


class SaleItemModel(Base):
    __tablename__ = "sale_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sale_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sales.id"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, item: SaleItem, sale_id: UUID) -> "SaleItemModel":
        return cls(
            id=str(item.id),
            sale_id=str(sale_id),
            product_id=str(item.product_id),
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            total_price=item.total_price,
            created_at=item.created_at,
        )

    def to_domain(self) -> SaleItem:
        return SaleItem(
            id=UUID(self.id),
            product_id=UUID(self.product_id),
            product_name=self.product_name,
            unit_price=self.unit_price,
            quantity=self.quantity,
            total_price=self.total_price,
            created_at=_as_utc(self.created_at),
        )


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cash_register_session_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("cash_register_sessions.id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(
        String(160), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True)
    expense_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, expense: Expense) -> "ExpenseModel":
        return cls(
            id=str(expense.id),
            cash_register_session_id=(
                str(expense.cash_register_session_id)
                if expense.cash_register_session_id is not None
                else None
            ),
            description=expense.description,
            amount=expense.amount,
            category=expense.category.value,
            payment_method=expense.payment_method.value,
            notes=expense.notes,
            created_by_user_id=str(expense.created_by_user_id),
            expense_date=expense.expense_date,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )

    def update_from_domain(self, expense: Expense) -> None:
        self.cash_register_session_id = (
            str(expense.cash_register_session_id)
            if expense.cash_register_session_id is not None
            else None
        )
        self.description = expense.description
        self.amount = expense.amount
        self.category = expense.category.value
        self.payment_method = expense.payment_method.value
        self.notes = expense.notes
        self.created_by_user_id = str(expense.created_by_user_id)
        self.expense_date = expense.expense_date
        self.created_at = expense.created_at
        self.updated_at = expense.updated_at

    def to_domain(self) -> Expense:
        return Expense(
            id=UUID(self.id),
            cash_register_session_id=(
                UUID(self.cash_register_session_id) if self.cash_register_session_id else None),
            description=self.description,
            amount=self.amount,
            category=ExpenseCategory(self.category),
            payment_method=PaymentMethod(self.payment_method),
            notes=self.notes,
            created_by_user_id=UUID(self.created_by_user_id),
            expense_date=_as_utc(self.expense_date),
            created_at=_as_utc(self.created_at),
            updated_at=_as_utc(self.updated_at),
        )


class SyncQueueEntryModel(Base):
    __tablename__ = "sync_queue"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_type: Mapped[str] = mapped_column(
        String(60), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[str] = mapped_column(String, nullable=False)
    sync_status: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True)
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, entry: SyncQueueEntry) -> "SyncQueueEntryModel":
        return cls(
            id=str(entry.id),
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            event_type=entry.event_type,
            payload=entry.payload,
            sync_status=entry.sync_status.value,
            retry_count=entry.retry_count,
            last_error=entry.last_error,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )

    def update_from_domain(self, entry: SyncQueueEntry) -> None:
        self.entity_type = entry.entity_type
        self.entity_id = entry.entity_id
        self.event_type = entry.event_type
        self.payload = entry.payload
        self.sync_status = entry.sync_status.value
        self.retry_count = entry.retry_count
        self.last_error = entry.last_error
        self.created_at = entry.created_at
        self.updated_at = entry.updated_at

    def to_domain(self) -> SyncQueueEntry:
        return SyncQueueEntry(
            id=UUID(self.id),
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            event_type=self.event_type,
            payload=self.payload,
            sync_status=SyncStatus(self.sync_status),
            retry_count=self.retry_count,
            last_error=self.last_error,
            created_at=_as_utc(self.created_at),
            updated_at=_as_utc(self.updated_at),
        )
