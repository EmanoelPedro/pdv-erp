from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_cash_register_service, get_current_owner_user, get_current_user
from app.domain.user import User
from app.schemas.cash_register import (
    CashRegisterSessionResponse,
    CloseCashRegisterRequest,
    OpenCashRegisterRequest,
)
from app.services.cash_register_service import CashRegisterService

router = APIRouter(prefix="/cash-register", tags=["cash-register"])


@router.post(
    "/open",
    response_model=CashRegisterSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def open_cash_register(
    payload: OpenCashRegisterRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[CashRegisterService, Depends(get_cash_register_service)],
) -> CashRegisterSessionResponse:
    session = service.open_session(payload.opening_amount)
    snapshot = service.get_session_snapshot(session.id)
    return CashRegisterSessionResponse.from_domain(
        snapshot.session,
        sales_amount=snapshot.metrics.sales_amount,
        sales_count=snapshot.metrics.sales_count,
        average_ticket_amount=snapshot.metrics.average_ticket_amount,
        total_received_amount=snapshot.metrics.total_received_amount,
        expenses_amount=snapshot.metrics.expenses_amount,
        cash_expenses_amount=snapshot.metrics.cash_expenses_amount,
        cash_sales_amount=snapshot.metrics.cash_sales_amount,
        pix_sales_amount=snapshot.metrics.pix_sales_amount,
        debit_card_sales_amount=snapshot.metrics.debit_card_sales_amount,
        credit_card_sales_amount=snapshot.metrics.credit_card_sales_amount,
        mixed_sales_amount=snapshot.metrics.mixed_sales_amount,
        cash_received_amount=snapshot.metrics.cash_received_amount,
        pix_received_amount=snapshot.metrics.pix_received_amount,
        debit_card_received_amount=snapshot.metrics.debit_card_received_amount,
        credit_card_received_amount=snapshot.metrics.credit_card_received_amount,
        last_sale_at=snapshot.metrics.last_sale_at,
    )


@router.get("/current", response_model=CashRegisterSessionResponse)
def get_current_cash_register(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[CashRegisterService, Depends(get_cash_register_service)],
) -> CashRegisterSessionResponse:
    snapshot = service.get_current_session_snapshot()
    return CashRegisterSessionResponse.from_domain(
        snapshot.session,
        sales_amount=snapshot.metrics.sales_amount,
        sales_count=snapshot.metrics.sales_count,
        average_ticket_amount=snapshot.metrics.average_ticket_amount,
        total_received_amount=snapshot.metrics.total_received_amount,
        expenses_amount=snapshot.metrics.expenses_amount,
        cash_expenses_amount=snapshot.metrics.cash_expenses_amount,
        cash_sales_amount=snapshot.metrics.cash_sales_amount,
        pix_sales_amount=snapshot.metrics.pix_sales_amount,
        debit_card_sales_amount=snapshot.metrics.debit_card_sales_amount,
        credit_card_sales_amount=snapshot.metrics.credit_card_sales_amount,
        mixed_sales_amount=snapshot.metrics.mixed_sales_amount,
        cash_received_amount=snapshot.metrics.cash_received_amount,
        pix_received_amount=snapshot.metrics.pix_received_amount,
        debit_card_received_amount=snapshot.metrics.debit_card_received_amount,
        credit_card_received_amount=snapshot.metrics.credit_card_received_amount,
        last_sale_at=snapshot.metrics.last_sale_at,
    )


@router.get("/history", response_model=list[CashRegisterSessionResponse])
def list_cash_register_history(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CashRegisterService, Depends(get_cash_register_service)],
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> list[CashRegisterSessionResponse]:
    snapshots = service.list_session_snapshots(start_date=start_date, end_date=end_date)
    return [
        CashRegisterSessionResponse.from_domain(
            snapshot.session,
            sales_amount=snapshot.metrics.sales_amount,
            sales_count=snapshot.metrics.sales_count,
            average_ticket_amount=snapshot.metrics.average_ticket_amount,
            total_received_amount=snapshot.metrics.total_received_amount,
            expenses_amount=snapshot.metrics.expenses_amount,
            cash_expenses_amount=snapshot.metrics.cash_expenses_amount,
            cash_sales_amount=snapshot.metrics.cash_sales_amount,
            pix_sales_amount=snapshot.metrics.pix_sales_amount,
            debit_card_sales_amount=snapshot.metrics.debit_card_sales_amount,
            credit_card_sales_amount=snapshot.metrics.credit_card_sales_amount,
            mixed_sales_amount=snapshot.metrics.mixed_sales_amount,
            cash_received_amount=snapshot.metrics.cash_received_amount,
            pix_received_amount=snapshot.metrics.pix_received_amount,
            debit_card_received_amount=snapshot.metrics.debit_card_received_amount,
            credit_card_received_amount=snapshot.metrics.credit_card_received_amount,
            last_sale_at=snapshot.metrics.last_sale_at,
        )
        for snapshot in snapshots
    ]


@router.get("/{session_id}", response_model=CashRegisterSessionResponse)
def get_cash_register_session(
    session_id: UUID,
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[CashRegisterService, Depends(get_cash_register_service)],
) -> CashRegisterSessionResponse:
    snapshot = service.get_session_snapshot(session_id)
    return CashRegisterSessionResponse.from_domain(
        snapshot.session,
        sales_amount=snapshot.metrics.sales_amount,
        sales_count=snapshot.metrics.sales_count,
        average_ticket_amount=snapshot.metrics.average_ticket_amount,
        total_received_amount=snapshot.metrics.total_received_amount,
        expenses_amount=snapshot.metrics.expenses_amount,
        cash_expenses_amount=snapshot.metrics.cash_expenses_amount,
        cash_sales_amount=snapshot.metrics.cash_sales_amount,
        pix_sales_amount=snapshot.metrics.pix_sales_amount,
        debit_card_sales_amount=snapshot.metrics.debit_card_sales_amount,
        credit_card_sales_amount=snapshot.metrics.credit_card_sales_amount,
        mixed_sales_amount=snapshot.metrics.mixed_sales_amount,
        cash_received_amount=snapshot.metrics.cash_received_amount,
        pix_received_amount=snapshot.metrics.pix_received_amount,
        debit_card_received_amount=snapshot.metrics.debit_card_received_amount,
        credit_card_received_amount=snapshot.metrics.credit_card_received_amount,
        last_sale_at=snapshot.metrics.last_sale_at,
    )


@router.post("/{session_id}/close", response_model=CashRegisterSessionResponse)
def close_cash_register(
    session_id: UUID,
    payload: CloseCashRegisterRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[CashRegisterService, Depends(get_cash_register_service)],
) -> CashRegisterSessionResponse:
    session = service.close_session(
        session_id=session_id,
        closing_amount=payload.closing_amount,
        actor=current_user,
        owner_pin=payload.owner_pin,
    )
    snapshot = service.get_session_snapshot(session.id)
    return CashRegisterSessionResponse.from_domain(
        snapshot.session,
        sales_amount=snapshot.metrics.sales_amount,
        sales_count=snapshot.metrics.sales_count,
        average_ticket_amount=snapshot.metrics.average_ticket_amount,
        total_received_amount=snapshot.metrics.total_received_amount,
        expenses_amount=snapshot.metrics.expenses_amount,
        cash_expenses_amount=snapshot.metrics.cash_expenses_amount,
        cash_sales_amount=snapshot.metrics.cash_sales_amount,
        pix_sales_amount=snapshot.metrics.pix_sales_amount,
        debit_card_sales_amount=snapshot.metrics.debit_card_sales_amount,
        credit_card_sales_amount=snapshot.metrics.credit_card_sales_amount,
        mixed_sales_amount=snapshot.metrics.mixed_sales_amount,
        cash_received_amount=snapshot.metrics.cash_received_amount,
        pix_received_amount=snapshot.metrics.pix_received_amount,
        debit_card_received_amount=snapshot.metrics.debit_card_received_amount,
        credit_card_received_amount=snapshot.metrics.credit_card_received_amount,
        last_sale_at=snapshot.metrics.last_sale_at,
    )
