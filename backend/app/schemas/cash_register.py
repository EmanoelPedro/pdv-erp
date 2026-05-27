from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.cash_register import CashRegisterSession, CashRegisterStatus
from app.schemas.auth import PinInput

MoneyInput = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]


class OpenCashRegisterRequest(BaseModel):
    opening_amount: MoneyInput


class CloseCashRegisterRequest(BaseModel):
    closing_amount: MoneyInput
    owner_pin: PinInput


class CashRegisterTotalsResponse(BaseModel):
    sales_amount: Decimal
    sales_count: int
    average_ticket_amount: Decimal
    total_received_amount: Decimal
    expenses_amount: Decimal
    cash_expenses_amount: Decimal
    expected_amount: Decimal
    cash_sales_amount: Decimal
    pix_sales_amount: Decimal
    debit_card_sales_amount: Decimal
    credit_card_sales_amount: Decimal
    mixed_sales_amount: Decimal
    cash_received_amount: Decimal
    pix_received_amount: Decimal
    debit_card_received_amount: Decimal
    credit_card_received_amount: Decimal
    last_sale_at: datetime | None


class CashRegisterHistoryFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class CashRegisterSessionResponse(BaseModel):
    id: UUID
    status: CashRegisterStatus
    opening_amount: Decimal
    expected_amount: Decimal
    closing_amount: Decimal | None
    difference_amount: Decimal | None
    opened_at: datetime
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    totals: CashRegisterTotalsResponse

    @classmethod
    def from_domain(
        cls,
        session: CashRegisterSession,
        *,
        sales_amount: Decimal = Decimal("0.00"),
        sales_count: int = 0,
        average_ticket_amount: Decimal = Decimal("0.00"),
        total_received_amount: Decimal = Decimal("0.00"),
        expenses_amount: Decimal = Decimal("0.00"),
        cash_expenses_amount: Decimal = Decimal("0.00"),
        cash_sales_amount: Decimal = Decimal("0.00"),
        pix_sales_amount: Decimal = Decimal("0.00"),
        debit_card_sales_amount: Decimal = Decimal("0.00"),
        credit_card_sales_amount: Decimal = Decimal("0.00"),
        mixed_sales_amount: Decimal = Decimal("0.00"),
        cash_received_amount: Decimal = Decimal("0.00"),
        pix_received_amount: Decimal = Decimal("0.00"),
        debit_card_received_amount: Decimal = Decimal("0.00"),
        credit_card_received_amount: Decimal = Decimal("0.00"),
        last_sale_at: datetime | None = None,
    ) -> "CashRegisterSessionResponse":
        return cls(
            id=session.id,
            status=session.status,
            opening_amount=session.opening_amount,
            expected_amount=session.expected_amount,
            closing_amount=session.closing_amount,
            difference_amount=session.difference_amount,
            opened_at=session.opened_at,
            closed_at=session.closed_at,
            created_at=session.created_at,
            updated_at=session.updated_at,
            totals=CashRegisterTotalsResponse(
                sales_amount=sales_amount,
                sales_count=sales_count,
                average_ticket_amount=average_ticket_amount,
                total_received_amount=total_received_amount,
                expenses_amount=expenses_amount,
                cash_expenses_amount=cash_expenses_amount,
                expected_amount=session.expected_amount,
                cash_sales_amount=cash_sales_amount,
                pix_sales_amount=pix_sales_amount,
                debit_card_sales_amount=debit_card_sales_amount,
                credit_card_sales_amount=credit_card_sales_amount,
                mixed_sales_amount=mixed_sales_amount,
                cash_received_amount=cash_received_amount,
                pix_received_amount=pix_received_amount,
                debit_card_received_amount=debit_card_received_amount,
                credit_card_received_amount=credit_card_received_amount,
                last_sale_at=last_sale_at,
            ),
        )
