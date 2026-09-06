from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.cash_register import CashRegisterSession
from app.domain.exceptions import (
    CashRegisterNotOpenError,
    ProductInactiveError,
    ProductNotFoundError,
)
from app.domain.sale import PaymentBreakdown, PaymentMethod, Sale, SaleItem
from app.domain.user import User
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.catalog_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository, SaleSessionMetrics


@dataclass(frozen=True, slots=True)
class SaleItemInput:
    product_id: UUID
    quantity: int


@dataclass(frozen=True, slots=True)
class CreateSaleResult:
    sale: Sale
    cash_register_session: CashRegisterSession


class SaleService:
    def __init__(
        self,
        sale_repository: SaleRepository,
        product_repository: ProductRepository,
        cash_register_repository: CashRegisterSessionRepository,
    ) -> None:
        self.sale_repository = sale_repository
        self.product_repository = product_repository
        self.cash_register_repository = cash_register_repository

    def create_sale(
        self,
        seller: User,
        items: list[SaleItemInput],
        payment_method: PaymentMethod,
        cash_amount: Decimal | None = None,
        pix_amount: Decimal | None = None,
        debit_card_amount: Decimal | None = None,
        credit_card_amount: Decimal | None = None,
    ) -> CreateSaleResult:
        open_session = self.cash_register_repository.get_open_session()
        if open_session is None:
            raise CashRegisterNotOpenError("An open cash register is required to make a sale.")

        products = self.product_repository.get_by_ids([item.product_id for item in items])
        product_map = {product.id: product for product in products}

        if len(product_map) != len(items):
            raise ProductNotFoundError("One or more products were not found.")

        sale_items: list[SaleItem] = []
        for item in items:
            product = product_map[item.product_id]
            if not product.is_active:
                raise ProductInactiveError("Inactive products cannot be sold.")
            sale_items.append(SaleItem.from_product(product, item.quantity))

        total_amount = sum((item.total_price for item in sale_items), start=Decimal("0.00"))
        payment = PaymentBreakdown.create(
            method=payment_method,
            total_amount=total_amount,
            cash_amount=cash_amount,
            pix_amount=pix_amount,
            debit_card_amount=debit_card_amount,
            credit_card_amount=credit_card_amount,
        )
        sale = Sale.create(
            cash_register_session_id=open_session.id,
            seller_user_id=seller.id,
            items=tuple(sale_items),
            payment=payment,
        )
        try:
            created_sale = self.sale_repository.create(sale)
            self.sale_repository.db.commit()
            return CreateSaleResult(
                sale=created_sale,
                cash_register_session=open_session,
            )
        except Exception:
            self.sale_repository.db.rollback()
            raise

    def get_session_metrics(self, session_id: UUID) -> SaleSessionMetrics:
        return self.sale_repository.get_session_metrics(session_id)
