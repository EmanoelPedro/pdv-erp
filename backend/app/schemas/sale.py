from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.domain.sale import PaymentMethod, Sale, SaleItem
from app.schemas.cash_register import CashRegisterSessionResponse

MoneyInput = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]


class SaleItemRequest(BaseModel):
    product_id: UUID
    quantity: Annotated[int, Field(ge=1, le=99)]


class CreateSaleRequest(BaseModel):
    items: Annotated[list[SaleItemRequest], Field(min_length=1)]
    payment_method: PaymentMethod
    cash_amount: MoneyInput | None = None
    pix_amount: MoneyInput | None = None
    debit_card_amount: MoneyInput | None = None
    credit_card_amount: MoneyInput | None = None

    @model_validator(mode="after")
    def validate_mixed_details(self) -> "CreateSaleRequest":
        if self.payment_method == PaymentMethod.MIXED:
            amounts = [
                self.cash_amount or Decimal("0.00"),
                self.pix_amount or Decimal("0.00"),
                self.debit_card_amount or Decimal("0.00"),
                self.credit_card_amount or Decimal("0.00"),
            ]
            if len([amount for amount in amounts if amount > 0]) < 2:
                msg = "Mixed payments require at least two positive payment amounts."
                raise ValueError(msg)
        return self


class SaleItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    created_at: datetime

    @classmethod
    def from_domain(cls, item: SaleItem) -> "SaleItemResponse":
        return cls(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            total_price=item.total_price,
            created_at=item.created_at,
        )


class SaleResponse(BaseModel):
    id: UUID
    cash_register_session_id: UUID
    seller_user_id: UUID
    payment_method: PaymentMethod
    subtotal_amount: Decimal
    total_amount: Decimal
    cash_amount: Decimal
    pix_amount: Decimal
    debit_card_amount: Decimal
    credit_card_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: list[SaleItemResponse]

    @classmethod
    def from_domain(cls, sale: Sale) -> "SaleResponse":
        return cls(
            id=sale.id,
            cash_register_session_id=sale.cash_register_session_id,
            seller_user_id=sale.seller_user_id,
            payment_method=sale.payment_method,
            subtotal_amount=sale.subtotal_amount,
            total_amount=sale.total_amount,
            cash_amount=sale.cash_amount,
            pix_amount=sale.pix_amount,
            debit_card_amount=sale.debit_card_amount,
            credit_card_amount=sale.credit_card_amount,
            created_at=sale.created_at,
            updated_at=sale.updated_at,
            items=[SaleItemResponse.from_domain(item) for item in sale.items],
        )


class CreateSaleResponse(BaseModel):
    sale: SaleResponse
    cash_register_session: CashRegisterSessionResponse
