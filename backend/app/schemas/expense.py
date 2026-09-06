from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.expense import Expense, ExpenseCategory
from app.domain.sale import PaymentMethod

PositiveMoneyInput = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]


class ExpenseBaseRequest(BaseModel):
    description: Annotated[str, Field(min_length=1, max_length=160)]
    amount: PositiveMoneyInput
    category: ExpenseCategory
    payment_method: PaymentMethod
    notes: Annotated[str | None, Field(max_length=500)] = None
    cash_register_session_id: UUID | None = None
    expense_date: datetime | None = None


class CreateExpenseRequest(ExpenseBaseRequest):
    pass


class UpdateExpenseRequest(ExpenseBaseRequest):
    pass


class ExpenseResponse(BaseModel):
    id: UUID
    cash_register_session_id: UUID | None
    description: str
    amount: Decimal
    category: ExpenseCategory
    payment_method: PaymentMethod
    notes: str | None
    created_by_user_id: UUID
    expense_date: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, expense: Expense) -> "ExpenseResponse":
        return cls(
            id=expense.id,
            cash_register_session_id=expense.cash_register_session_id,
            description=expense.description,
            amount=expense.amount,
            category=expense.category,
            payment_method=expense.payment_method,
            notes=expense.notes,
            created_by_user_id=expense.created_by_user_id,
            expense_date=expense.expense_date,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )


class ExpenseListFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    category: ExpenseCategory | None = None
    cash_register_session_id: UUID | None = None
