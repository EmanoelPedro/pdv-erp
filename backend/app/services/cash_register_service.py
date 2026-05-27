from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from app.domain.cash_register import CashRegisterSession
from app.domain.exceptions import (
    CashRegisterAlreadyOpenError,
    CashRegisterNotFoundError,
    InvalidOwnerPinError,
    OwnerPermissionRequiredError,
)
from app.domain.shared import normalize_money
from app.domain.user import User, UserRole
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.expense_repository import ExpenseRepository, ExpenseSessionMetrics
from app.repositories.sale_repository import SaleRepository, SaleSessionMetrics
from app.services.security import verify_pin


@dataclass(frozen=True, slots=True)
class CashRegisterSessionMetrics:
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


@dataclass(frozen=True, slots=True)
class CashRegisterSessionSnapshot:
    session: CashRegisterSession
    metrics: CashRegisterSessionMetrics


class CashRegisterService:
    def __init__(
        self,
        repository: CashRegisterSessionRepository,
        sale_repository: SaleRepository,
        expense_repository: ExpenseRepository,
    ) -> None:
        self.repository = repository
        self.sale_repository = sale_repository
        self.expense_repository = expense_repository

    def open_session(self, opening_amount: Decimal) -> CashRegisterSession:
        current_session = self.repository.get_open_session()
        if current_session is not None:
            raise CashRegisterAlreadyOpenError(
                "There is already an open cash register session.",
            )

        session = CashRegisterSession.open(opening_amount=opening_amount)
        try:
            created_session = self.repository.create(session)
            self.repository.db.commit()
            return created_session
        except Exception:
            self.repository.db.rollback()
            raise

    def get_current_session(self) -> CashRegisterSession:
        return self.get_current_session_snapshot().session

    def get_current_session_snapshot(self) -> CashRegisterSessionSnapshot:
        session = self.repository.get_open_session()
        if session is None:
            raise CashRegisterNotFoundError(
                "No open cash register session was found.")

        return self._build_snapshot(session)

    def get_session_snapshot(self, session_id: UUID) -> CashRegisterSessionSnapshot:
        session = self.repository.get_by_id(session_id)
        if session is None:
            raise CashRegisterNotFoundError(
                "Cash register session was not found.")

        return self._build_snapshot(session)

    def list_session_snapshots(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[CashRegisterSessionSnapshot]:
        sessions = self.repository.list_all(
            start_date=start_date, end_date=end_date)
        return [self._build_snapshot(session) for session in sessions]

    def close_session(
        self,
        session_id: UUID,
        closing_amount: Decimal,
        actor: User,
        owner_pin: str,
    ) -> CashRegisterSession:
        self._require_owner(actor)
        self._require_valid_owner_pin(actor, owner_pin)

        session_snapshot = self.get_session_snapshot(session_id)
        closed_session = session_snapshot.session.close(
            closing_amount=closing_amount)
        try:
            updated_session = self.repository.update(closed_session)
            self.repository.db.commit()
            return updated_session
        except Exception:
            self.repository.db.rollback()
            raise

    def _require_owner(self, actor: User) -> None:
        if actor.role != UserRole.OWNER:
            raise OwnerPermissionRequiredError(
                "Owner approval is required for this action.",
            )

    def _require_valid_owner_pin(self, actor: User, owner_pin: str) -> None:
        if not verify_pin(owner_pin, actor.pin_hash):
            raise InvalidOwnerPinError("Invalid owner PIN.")

    def get_session_metrics(self, session_id: UUID) -> CashRegisterSessionMetrics:
        return self.get_session_snapshot(session_id).metrics

    def _build_snapshot(self, session: CashRegisterSession) -> CashRegisterSessionSnapshot:
        sale_metrics = self.sale_repository.get_session_metrics(session.id)
        expense_metrics = self.expense_repository.get_session_metrics(
            session.id)
        expected_amount = normalize_money(
            session.opening_amount
            + sale_metrics.cash_received_amount
            - expense_metrics.cash_amount,
        )
        difference_amount = session.difference_amount
        if session.closing_amount is not None:
            difference_amount = normalize_money(
                session.closing_amount - expected_amount)

        hydrated_session = replace(
            session,
            expected_amount=expected_amount,
            difference_amount=difference_amount,
        )
        metrics = self._compose_metrics(
            sale_metrics, expense_metrics, expected_amount)
        return CashRegisterSessionSnapshot(session=hydrated_session, metrics=metrics)

    def _compose_metrics(
        self,
        sale_metrics: SaleSessionMetrics,
        expense_metrics: ExpenseSessionMetrics,
        expected_amount: Decimal,
    ) -> CashRegisterSessionMetrics:
        return CashRegisterSessionMetrics(
            sales_amount=sale_metrics.sales_amount,
            sales_count=sale_metrics.sales_count,
            average_ticket_amount=sale_metrics.average_ticket_amount,
            total_received_amount=sale_metrics.total_received_amount,
            expenses_amount=expense_metrics.total_amount,
            cash_expenses_amount=expense_metrics.cash_amount,
            expected_amount=expected_amount,
            cash_sales_amount=sale_metrics.cash_sales_amount,
            pix_sales_amount=sale_metrics.pix_sales_amount,
            debit_card_sales_amount=sale_metrics.debit_card_sales_amount,
            credit_card_sales_amount=sale_metrics.credit_card_sales_amount,
            mixed_sales_amount=sale_metrics.mixed_sales_amount,
            cash_received_amount=sale_metrics.cash_received_amount,
            pix_received_amount=sale_metrics.pix_received_amount,
            debit_card_received_amount=sale_metrics.debit_card_received_amount,
            credit_card_received_amount=sale_metrics.credit_card_received_amount,
            last_sale_at=sale_metrics.last_sale_at,
        )
