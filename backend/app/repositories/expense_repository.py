from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.database.models import ExpenseModel
from app.domain.expense import Expense, ExpenseCategory
from app.domain.sale import PaymentMethod
from app.domain.shared import normalize_money


@dataclass(frozen=True, slots=True)
class ExpenseSessionMetrics:
    total_amount: Decimal
    cash_amount: Decimal


class ExpenseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, expense: Expense) -> Expense:
        model = ExpenseModel.from_domain(expense)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def get_by_id(self, expense_id: UUID) -> Expense | None:
        model = self.db.get(ExpenseModel, str(expense_id))
        return model.to_domain() if model else None

    def list_all(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        category: ExpenseCategory | None = None,
        cash_register_session_id: UUID | None = None,
    ) -> list[Expense]:
        statement = select(ExpenseModel).order_by(ExpenseModel.expense_date.desc())

        if start_date is not None:
            occurred_from = datetime.combine(start_date, time.min, tzinfo=UTC)
            statement = statement.where(ExpenseModel.expense_date >= occurred_from)

        if end_date is not None:
            occurred_to = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=UTC)
            statement = statement.where(ExpenseModel.expense_date < occurred_to)

        if category is not None:
            statement = statement.where(ExpenseModel.category == category.value)

        if cash_register_session_id is not None:
            statement = statement.where(
                ExpenseModel.cash_register_session_id == str(cash_register_session_id),
            )

        return [model.to_domain() for model in self.db.scalars(statement)]

    def update(self, expense: Expense) -> Expense:
        model = self.db.get(ExpenseModel, str(expense.id))
        if model is None:
            msg = "Expense was not found."
            raise LookupError(msg)

        model.update_from_domain(expense)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return model.to_domain()

    def delete(self, expense_id: UUID) -> None:
        model = self.db.get(ExpenseModel, str(expense_id))
        if model is None:
            return

        self.db.delete(model)
        self.db.flush()

    def get_session_metrics(self, session_id: UUID) -> ExpenseSessionMetrics:
        statement = select(
            func.coalesce(func.sum(ExpenseModel.amount), 0),
            func.coalesce(
                func.sum(
                    case(
                        (
                            ExpenseModel.payment_method == PaymentMethod.CASH.value,
                            ExpenseModel.amount,
                        ),
                        else_=0,
                    ),
                ),
                0,
            ),
        ).where(ExpenseModel.cash_register_session_id == str(session_id))

        total_amount_raw, cash_amount_raw = self.db.execute(statement).one()
        return ExpenseSessionMetrics(
            total_amount=normalize_money(Decimal(str(total_amount_raw or 0))),
            cash_amount=normalize_money(Decimal(str(cash_amount_raw or 0))),
        )
