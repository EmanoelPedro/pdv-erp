from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.exceptions import InvalidExpenseAmountError
from app.domain.sale import PaymentMethod
from app.domain.shared import ensure_utc, normalize_money, utc_now


class ExpenseCategory(StrEnum):
    INGREDIENTS = "INGREDIENTS"
    PACKAGING = "PACKAGING"
    UTILITIES = "UTILITIES"
    MAINTENANCE = "MAINTENANCE"
    CLEANING = "CLEANING"
    WITHDRAWAL = "WITHDRAWAL"
    PERSONAL_USE = "PERSONAL_USE"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class Expense:
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
    def create(
        cls,
        *,
        description: str,
        amount: Decimal,
        category: ExpenseCategory,
        payment_method: PaymentMethod,
        created_by_user_id: UUID,
        cash_register_session_id: UUID | None = None,
        notes: str | None = None,
        expense_date: datetime | None = None,
        created_at: datetime | None = None,
    ) -> "Expense":
        normalized_amount = normalize_money(amount)
        if normalized_amount <= Decimal("0.00"):
            raise InvalidExpenseAmountError("Expense amount must be greater than zero.")

        timestamp = ensure_utc(created_at or utc_now())
        occurred_at = ensure_utc(expense_date or timestamp)
        normalized_description = description.strip()
        normalized_notes = notes.strip() or None if notes else None

        return cls(
            id=uuid4(),
            cash_register_session_id=cash_register_session_id,
            description=normalized_description,
            amount=normalized_amount,
            category=category,
            payment_method=payment_method,
            notes=normalized_notes,
            created_by_user_id=created_by_user_id,
            expense_date=occurred_at,
            created_at=timestamp,
            updated_at=timestamp,
        )
