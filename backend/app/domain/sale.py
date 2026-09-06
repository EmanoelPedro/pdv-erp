from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.catalog import Product
from app.domain.exceptions import InvalidPaymentError
from app.domain.shared import ensure_utc, normalize_money, utc_now


class PaymentMethod(StrEnum):
    CASH = "CASH"
    PIX = "PIX"
    DEBIT_CARD = "DEBIT_CARD"
    CREDIT_CARD = "CREDIT_CARD"
    MIXED = "MIXED"


class SaleStatus(StrEnum):
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class PaymentBreakdown:
    method: PaymentMethod
    total_amount: Decimal
    cash_amount: Decimal
    pix_amount: Decimal
    debit_card_amount: Decimal
    credit_card_amount: Decimal

    @classmethod
    def create(
        cls,
        method: PaymentMethod,
        total_amount: Decimal,
        cash_amount: Decimal | None = None,
        pix_amount: Decimal | None = None,
        debit_card_amount: Decimal | None = None,
        credit_card_amount: Decimal | None = None,
    ) -> "PaymentBreakdown":
        normalized_total = normalize_money(total_amount)
        amounts = {
            PaymentMethod.CASH: normalize_money(cash_amount or Decimal("0.00")),
            PaymentMethod.PIX: normalize_money(pix_amount or Decimal("0.00")),
            PaymentMethod.DEBIT_CARD: normalize_money(debit_card_amount or Decimal("0.00")),
            PaymentMethod.CREDIT_CARD: normalize_money(credit_card_amount or Decimal("0.00")),
        }

        if method != PaymentMethod.MIXED:
            for payment_method in amounts:
                amounts[payment_method] = (
                    normalized_total if payment_method == method else Decimal("0.00")
                )
        else:
            positive_methods = [amount for amount in amounts.values() if amount > 0]
            if len(positive_methods) < 2:
                raise InvalidPaymentError(
                    "Mixed payments must include at least two payment amounts.",
                )

            total_breakdown = normalize_money(sum(amounts.values(), start=Decimal("0.00")))
            if total_breakdown != normalized_total:
                raise InvalidPaymentError(
                    "Mixed payment amounts must add up to the sale total.",
                )

        return cls(
            method=method,
            total_amount=normalized_total,
            cash_amount=amounts[PaymentMethod.CASH],
            pix_amount=amounts[PaymentMethod.PIX],
            debit_card_amount=amounts[PaymentMethod.DEBIT_CARD],
            credit_card_amount=amounts[PaymentMethod.CREDIT_CARD],
        )


@dataclass(frozen=True, slots=True)
class SaleItem:
    id: UUID
    product_id: UUID
    product_name: str
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    created_at: datetime

    @classmethod
    def from_product(
        cls,
        product: Product,
        quantity: int,
        created_at: datetime | None = None,
    ) -> "SaleItem":
        occurred_at = ensure_utc(created_at or utc_now())
        total_price = normalize_money(product.price * quantity)
        return cls(
            id=uuid4(),
            product_id=product.id,
            product_name=product.name,
            unit_price=product.price,
            quantity=quantity,
            total_price=total_price,
            created_at=occurred_at,
        )


@dataclass(frozen=True, slots=True)
class Sale:
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
    status: SaleStatus
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None
    items: tuple[SaleItem, ...]

    @classmethod
    def create(
        cls,
        cash_register_session_id: UUID,
        seller_user_id: UUID,
        items: tuple[SaleItem, ...],
        payment: PaymentBreakdown,
        created_at: datetime | None = None,
    ) -> "Sale":
        occurred_at = ensure_utc(created_at or utc_now())
        subtotal_amount = normalize_money(
            sum((item.total_price for item in items), start=Decimal("0.00")),
        )
        if subtotal_amount != payment.total_amount:
            raise InvalidPaymentError("Payment total must match the cart total.")

        return cls(
            id=uuid4(),
            cash_register_session_id=cash_register_session_id,
            seller_user_id=seller_user_id,
            payment_method=payment.method,
            subtotal_amount=subtotal_amount,
            total_amount=payment.total_amount,
            cash_amount=payment.cash_amount,
            pix_amount=payment.pix_amount,
            debit_card_amount=payment.debit_card_amount,
            credit_card_amount=payment.credit_card_amount,
            status=SaleStatus.COMPLETED,
            created_at=occurred_at,
            updated_at=occurred_at,
            cancelled_at=None,
            items=items,
        )
