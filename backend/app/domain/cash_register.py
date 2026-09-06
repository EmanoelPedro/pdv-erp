from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.exceptions import CashRegisterAlreadyClosedError
from app.domain.shared import ensure_utc, normalize_money, utc_now


class CashRegisterStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass(frozen=True, slots=True)
class CashRegisterSession:
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

    @classmethod
    def open(
        cls,
        opening_amount: Decimal,
        opened_at: datetime | None = None,
    ) -> "CashRegisterSession":
        occurred_at = ensure_utc(opened_at or utc_now())
        normalized_opening = normalize_money(opening_amount)

        return cls(
            id=uuid4(),
            status=CashRegisterStatus.OPEN,
            opening_amount=normalized_opening,
            expected_amount=normalized_opening,
            closing_amount=None,
            difference_amount=None,
            opened_at=occurred_at,
            closed_at=None,
            created_at=occurred_at,
            updated_at=occurred_at,
        )

    def close(
        self,
        closing_amount: Decimal,
        closed_at: datetime | None = None,
    ) -> "CashRegisterSession":
        if self.status == CashRegisterStatus.CLOSED:
            raise CashRegisterAlreadyClosedError(
                "Cash register session is already closed.",
            )

        occurred_at = ensure_utc(closed_at or utc_now())
        normalized_closing = normalize_money(closing_amount)
        difference_amount = normalize_money(normalized_closing - self.expected_amount)

        return replace(
            self,
            status=CashRegisterStatus.CLOSED,
            closing_amount=normalized_closing,
            difference_amount=difference_amount,
            closed_at=occurred_at,
            updated_at=occurred_at,
        )

    def register_cash_entry(
        self,
        cash_amount: Decimal,
        occurred_at: datetime | None = None,
    ) -> "CashRegisterSession":
        if self.status == CashRegisterStatus.CLOSED:
            raise CashRegisterAlreadyClosedError(
                "Cannot update a closed cash register session.",
            )

        entry_time = ensure_utc(occurred_at or utc_now())
        normalized_cash = normalize_money(cash_amount)

        return replace(
            self,
            expected_amount=normalize_money(self.expected_amount + normalized_cash),
            updated_at=entry_time,
        )
