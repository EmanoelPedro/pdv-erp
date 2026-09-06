from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_cash_register_service, get_current_user, get_sale_service
from app.domain.user import User
from app.schemas.cash_register import CashRegisterSessionResponse
from app.schemas.sale import CreateSaleRequest, CreateSaleResponse, SaleResponse
from app.services.cash_register_service import CashRegisterService
from app.services.sale_service import SaleItemInput, SaleService

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=CreateSaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    payload: CreateSaleRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SaleService, Depends(get_sale_service)],
    cash_register_service: Annotated[CashRegisterService, Depends(get_cash_register_service)],
) -> CreateSaleResponse:
    result = service.create_sale(
        seller=current_user,
        items=[
            SaleItemInput(product_id=item.product_id, quantity=item.quantity)
            for item in payload.items
        ],
        payment_method=payload.payment_method,
        cash_amount=payload.cash_amount,
        pix_amount=payload.pix_amount,
        debit_card_amount=payload.debit_card_amount,
        credit_card_amount=payload.credit_card_amount,
    )
    snapshot = cash_register_service.get_session_snapshot(result.cash_register_session.id)
    return CreateSaleResponse(
        sale=SaleResponse.from_domain(result.sale),
        cash_register_session=CashRegisterSessionResponse.from_domain(
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
        ),
    )
