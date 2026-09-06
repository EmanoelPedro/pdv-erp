from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from app.domain.cash_register import CashRegisterStatus
from app.domain.exceptions import (
    CashRegisterNotFoundError,
    ExpenseImmutableError,
    ExpenseNotFoundError,
)
from app.domain.expense import Expense, ExpenseCategory
from app.domain.sale import PaymentMethod
from app.domain.shared import utc_now
from app.domain.user import User
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.expense_repository import ExpenseRepository
from app.services.auth_service import AuthService


class ExpenseService:
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        cash_register_repository: CashRegisterSessionRepository,
        auth_service: AuthService,
    ) -> None:
        self.expense_repository = expense_repository
        self.cash_register_repository = cash_register_repository
        self.auth_service = auth_service

    def create_expense(
        self,
        *,
        description: str,
        amount: Decimal,
        category: ExpenseCategory,
        payment_method: PaymentMethod,
        created_by: User,
        cash_register_session_id: UUID | None = None,
        notes: str | None = None,
        expense_date: datetime | None = None,
    ) -> Expense:
        self.auth_service.require_owner(created_by)
        self._ensure_session_mutable(cash_register_session_id)

        expense = Expense.create(
            description=description,
            amount=amount,
            category=category,
            payment_method=payment_method,
            created_by_user_id=created_by.id,
            cash_register_session_id=cash_register_session_id,
            notes=notes,
            expense_date=expense_date,
        )
        try:
            created_expense = self.expense_repository.create(expense)
            self.expense_repository.db.commit()
            return created_expense
        except Exception:
            self.expense_repository.db.rollback()
            raise

    def list_expenses(
        self,
        *,
        actor: User,
        start_date: date | None = None,
        end_date: date | None = None,
        category: ExpenseCategory | None = None,
        cash_register_session_id: UUID | None = None,
    ) -> list[Expense]:
        self.auth_service.require_owner(actor)
        return self.expense_repository.list_all(
            start_date=start_date,
            end_date=end_date,
            category=category,
            cash_register_session_id=cash_register_session_id,
        )

    def get_expense(self, expense_id: UUID, actor: User) -> Expense:
        self.auth_service.require_owner(actor)
        expense = self.expense_repository.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError("Expense was not found.")
        return expense

    def update_expense(
        self,
        expense_id: UUID,
        *,
        description: str,
        amount: Decimal,
        category: ExpenseCategory,
        payment_method: PaymentMethod,
        actor: User,
        cash_register_session_id: UUID | None = None,
        notes: str | None = None,
        expense_date: datetime | None = None,
    ) -> Expense:
        self.auth_service.require_owner(actor)
        expense = self.expense_repository.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError("Expense was not found.")

        self._ensure_session_mutable(expense.cash_register_session_id)
        self._ensure_session_mutable(cash_register_session_id)

        updated_expense = replace(
            expense,
            cash_register_session_id=cash_register_session_id,
            description=description.strip(),
            amount=Expense.create(
                description=description,
                amount=amount,
                category=category,
                payment_method=payment_method,
                created_by_user_id=expense.created_by_user_id,
                cash_register_session_id=cash_register_session_id,
                notes=notes,
                expense_date=expense_date or expense.expense_date,
                created_at=expense.created_at,
            ).amount,
            category=category,
            payment_method=payment_method,
            notes=notes.strip() or None if notes else None,
            expense_date=expense_date or expense.expense_date,
            updated_at=utc_now(),
        )
        try:
            persisted_expense = self.expense_repository.update(updated_expense)
            self.expense_repository.db.commit()
            return persisted_expense
        except Exception:
            self.expense_repository.db.rollback()
            raise

    def delete_expense(self, expense_id: UUID, actor: User) -> None:
        self.auth_service.require_owner(actor)
        expense = self.expense_repository.get_by_id(expense_id)
        if expense is None:
            raise ExpenseNotFoundError("Expense was not found.")

        self._ensure_session_mutable(expense.cash_register_session_id)
        try:
            self.expense_repository.delete(expense_id)
            self.expense_repository.db.commit()
        except Exception:
            self.expense_repository.db.rollback()
            raise

    def _ensure_session_mutable(self, cash_register_session_id: UUID | None) -> None:
        if cash_register_session_id is None:
            return

        session = self.cash_register_repository.get_by_id(cash_register_session_id)
        if session is None:
            raise CashRegisterNotFoundError("Cash register session was not found.")
        if session.status == CashRegisterStatus.CLOSED:
            raise ExpenseImmutableError(
                "Expenses linked to a closed cash register session cannot be changed.",
            )
