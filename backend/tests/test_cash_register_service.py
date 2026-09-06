from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.domain.cash_register import CashRegisterStatus
from app.domain.catalog import Category, Product
from app.domain.exceptions import (
    CashRegisterAlreadyClosedError,
    CashRegisterAlreadyOpenError,
    InvalidOwnerPinError,
    OwnerPermissionRequiredError,
)
from app.domain.expense import ExpenseCategory
from app.domain.sale import PaymentMethod
from app.domain.user import User, UserRole
from app.repositories.auth_session_repository import AuthSessionRepository
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.catalog_repository import CategoryRepository, ProductRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.cash_register_service import CashRegisterService
from app.services.expense_service import ExpenseService
from app.services.sale_service import SaleItemInput, SaleService
from app.services.security import hash_pin


@pytest.fixture
def cash_register_service(db_session: Session) -> CashRegisterService:
    repository = CashRegisterSessionRepository(db_session)
    return CashRegisterService(
        repository=repository,
        sale_repository=SaleRepository(db_session),
        expense_repository=ExpenseRepository(db_session),
    )


@pytest.fixture
def auth_service(db_session: Session) -> AuthService:
    return AuthService(
        user_repository=UserRepository(db_session),
        auth_session_repository=AuthSessionRepository(db_session),
        session_days=30,
    )


@pytest.fixture
def expense_service(db_session: Session, auth_service: AuthService) -> ExpenseService:
    return ExpenseService(
        expense_repository=ExpenseRepository(db_session),
        cash_register_repository=CashRegisterSessionRepository(db_session),
        auth_service=auth_service,
    )


@pytest.fixture
def sale_service(db_session: Session) -> SaleService:
    return SaleService(
        sale_repository=SaleRepository(db_session),
        product_repository=ProductRepository(db_session),
        cash_register_repository=CashRegisterSessionRepository(db_session),
    )


@pytest.fixture
def owner_user(db_session: Session) -> User:
    user = User.create(
        full_name="Owner User",
        username="owner",
        role=UserRole.OWNER,
        pin_hash=hash_pin("1234"),
    )
    created_user = UserRepository(db_session).create(user)
    db_session.commit()
    return created_user


@pytest.fixture
def employee_user(db_session: Session) -> User:
    user = User.create(
        full_name="Employee User",
        username="employee",
        role=UserRole.EMPLOYEE,
        pin_hash=hash_pin("5678"),
    )
    created_user = UserRepository(db_session).create(user)
    db_session.commit()
    return created_user


def _create_product(db_session: Session, name: str = "Product", price: str = "100.00") -> Product:
    category_repository = CategoryRepository(db_session)
    product_repository = ProductRepository(db_session)
    category = category_repository.create(Category.create(name="Categoria Teste"))
    product = product_repository.create(
        Product.create(
            category_id=category.id,
            name=name,
            price=Decimal(price),
        ),
    )
    db_session.commit()
    return product


def test_open_cash_register_success(
    cash_register_service: CashRegisterService,
) -> None:
    session = cash_register_service.open_session(Decimal("150.00"))

    assert session.status == CashRegisterStatus.OPEN
    assert session.opening_amount == Decimal("150.00")
    assert session.expected_amount == Decimal("150.00")
    assert session.closed_at is None
    assert session.opened_at.tzinfo is not None


def test_cannot_open_two_sessions(
    cash_register_service: CashRegisterService,
) -> None:
    cash_register_service.open_session(Decimal("50.00"))

    with pytest.raises(CashRegisterAlreadyOpenError):
        cash_register_service.open_session(Decimal("10.00"))


def test_close_cash_register_success(
    cash_register_service: CashRegisterService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("100.00"))

    closed_session = cash_register_service.close_session(
        session_id=open_session.id,
        closing_amount=Decimal("100.00"),
        actor=owner_user,
        owner_pin="1234",
    )

    assert closed_session.status == CashRegisterStatus.CLOSED
    assert closed_session.closing_amount == Decimal("100.00")
    assert closed_session.difference_amount == Decimal("0.00")
    assert closed_session.closed_at is not None
    assert closed_session.closed_at.tzinfo is not None


def test_cannot_close_twice(
    cash_register_service: CashRegisterService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("75.00"))
    cash_register_service.close_session(
        session_id=open_session.id,
        closing_amount=Decimal("75.00"),
        actor=owner_user,
        owner_pin="1234",
    )

    with pytest.raises(CashRegisterAlreadyClosedError):
        cash_register_service.close_session(
            session_id=open_session.id,
            closing_amount=Decimal("75.00"),
            actor=owner_user,
            owner_pin="1234",
        )


def test_difference_calculation(
    cash_register_service: CashRegisterService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("80.00"))

    closed_session = cash_register_service.close_session(
        session_id=open_session.id,
        closing_amount=Decimal("92.35"),
        actor=owner_user,
        owner_pin="1234",
    )

    assert closed_session.expected_amount == Decimal("80.00")
    assert closed_session.difference_amount == Decimal("12.35")


def test_close_requires_owner_pin(
    cash_register_service: CashRegisterService,
    employee_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("80.00"))

    with pytest.raises(OwnerPermissionRequiredError):
        cash_register_service.close_session(
            session_id=open_session.id,
            closing_amount=Decimal("80.00"),
            actor=employee_user,
            owner_pin="5678",
        )


def test_close_requires_valid_owner_pin(
    cash_register_service: CashRegisterService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("80.00"))

    with pytest.raises(InvalidOwnerPinError):
        cash_register_service.close_session(
            session_id=open_session.id,
            closing_amount=Decimal("80.00"),
            actor=owner_user,
            owner_pin="0000",
        )


def test_expected_cash_uses_only_cash_movements(
    db_session: Session,
    cash_register_service: CashRegisterService,
    sale_service: SaleService,
    expense_service: ExpenseService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("300.00"))
    product = _create_product(db_session, name="Pastel", price="100.00")

    sale_service.create_sale(
        seller=owner_user,
        items=[SaleItemInput(product_id=product.id, quantity=7)],
        payment_method=PaymentMethod.CASH,
    )
    sale_service.create_sale(
        seller=owner_user,
        items=[SaleItemInput(product_id=product.id, quantity=4)],
        payment_method=PaymentMethod.PIX,
    )
    sale_service.create_sale(
        seller=owner_user,
        items=[SaleItemInput(product_id=product.id, quantity=2)],
        payment_method=PaymentMethod.CREDIT_CARD,
    )
    expense_service.create_expense(
        description="Compra de insumos",
        amount=Decimal("150.00"),
        category=ExpenseCategory.INGREDIENTS,
        payment_method=PaymentMethod.CASH,
        created_by=owner_user,
        cash_register_session_id=open_session.id,
    )

    snapshot = cash_register_service.get_session_snapshot(open_session.id)

    assert snapshot.metrics.cash_received_amount == Decimal("700.00")
    assert snapshot.metrics.pix_received_amount == Decimal("400.00")
    assert snapshot.metrics.credit_card_received_amount == Decimal("200.00")
    assert snapshot.metrics.cash_expenses_amount == Decimal("150.00")
    assert snapshot.session.expected_amount == Decimal("850.00")


def test_closing_difference_uses_recalculated_expected_amount(
    db_session: Session,
    cash_register_service: CashRegisterService,
    sale_service: SaleService,
    expense_service: ExpenseService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("100.00"))
    product = _create_product(db_session, name="Caldo", price="50.00")

    sale_service.create_sale(
        seller=owner_user,
        items=[SaleItemInput(product_id=product.id, quantity=4)],
        payment_method=PaymentMethod.MIXED,
        cash_amount=Decimal("60.00"),
        pix_amount=Decimal("140.00"),
    )
    expense_service.create_expense(
        description="Retirada",
        amount=Decimal("20.00"),
        category=ExpenseCategory.WITHDRAWAL,
        payment_method=PaymentMethod.CASH,
        created_by=owner_user,
        cash_register_session_id=open_session.id,
    )

    closed_session = cash_register_service.close_session(
        session_id=open_session.id,
        closing_amount=Decimal("150.00"),
        actor=owner_user,
        owner_pin="1234",
    )

    assert closed_session.expected_amount == Decimal("140.00")
    assert closed_session.difference_amount == Decimal("10.00")
