from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.domain.cash_register import CashRegisterStatus
from app.domain.exceptions import (
    ExpenseImmutableError,
    InvalidExpenseAmountError,
    OwnerPermissionRequiredError,
)
from app.domain.expense import ExpenseCategory
from app.domain.sale import PaymentMethod
from app.domain.user import User, UserRole
from app.repositories.auth_session_repository import AuthSessionRepository
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.cash_register_service import CashRegisterService
from app.services.expense_service import ExpenseService
from app.services.security import hash_pin


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
def cash_register_service(db_session: Session) -> CashRegisterService:
    return CashRegisterService(
        repository=CashRegisterSessionRepository(db_session),
        sale_repository=__import__("app.repositories.sale_repository", fromlist=[
                                   "SaleRepository"]).SaleRepository(db_session),
        expense_repository=ExpenseRepository(db_session),
    )


@pytest.fixture
def owner_user(db_session: Session) -> User:
    created_user = UserRepository(db_session).create(
        User.create(
            full_name="Owner User",
            username="owner",
            role=UserRole.OWNER,
            pin_hash=hash_pin("1234"),
        ),
    )
    db_session.commit()
    return created_user


@pytest.fixture
def employee_user(db_session: Session) -> User:
    created_user = UserRepository(db_session).create(
        User.create(
            full_name="Employee User",
            username="employee",
            role=UserRole.EMPLOYEE,
            pin_hash=hash_pin("5678"),
        ),
    )
    db_session.commit()
    return created_user


def test_create_expense_success(
    expense_service: ExpenseService,
    cash_register_service: CashRegisterService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("200.00"))

    expense = expense_service.create_expense(
        description="Compra de embalagem",
        amount=Decimal("45.00"),
        category=ExpenseCategory.PACKAGING,
        payment_method=PaymentMethod.CASH,
        created_by=owner_user,
        cash_register_session_id=open_session.id,
        notes="Reposicao",
    )

    assert expense.description == "Compra de embalagem"
    assert expense.amount == Decimal("45.00")
    assert expense.cash_register_session_id == open_session.id


def test_expense_amount_must_be_positive(
    expense_service: ExpenseService,
    owner_user: User,
) -> None:
    with pytest.raises(InvalidExpenseAmountError):
        expense_service.create_expense(
            description="Taxa",
            amount=Decimal("0.00"),
            category=ExpenseCategory.OTHER,
            payment_method=PaymentMethod.PIX,
            created_by=owner_user,
        )


def test_only_owner_can_create_expense(
    expense_service: ExpenseService,
    employee_user: User,
) -> None:
    with pytest.raises(OwnerPermissionRequiredError):
        expense_service.create_expense(
            description="Compra",
            amount=Decimal("10.00"),
            category=ExpenseCategory.CLEANING,
            payment_method=PaymentMethod.CASH,
            created_by=employee_user,
        )


def test_expense_linked_to_closed_session_becomes_immutable(
    expense_service: ExpenseService,
    cash_register_service: CashRegisterService,
    owner_user: User,
) -> None:
    open_session = cash_register_service.open_session(Decimal("100.00"))
    expense = expense_service.create_expense(
        description="Retirada pessoal",
        amount=Decimal("30.00"),
        category=ExpenseCategory.PERSONAL_USE,
        payment_method=PaymentMethod.CASH,
        created_by=owner_user,
        cash_register_session_id=open_session.id,
    )
    closed_session = cash_register_service.close_session(
        session_id=open_session.id,
        closing_amount=Decimal("70.00"),
        actor=owner_user,
        owner_pin="1234",
    )

    assert closed_session.status == CashRegisterStatus.CLOSED

    with pytest.raises(ExpenseImmutableError):
        expense_service.update_expense(
            expense.id,
            description="Retirada ajustada",
            amount=Decimal("25.00"),
            category=ExpenseCategory.PERSONAL_USE,
            payment_method=PaymentMethod.CASH,
            actor=owner_user,
            cash_register_session_id=open_session.id,
        )
