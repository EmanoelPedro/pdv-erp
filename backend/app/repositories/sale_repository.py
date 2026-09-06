from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.database.models import SaleItemModel, SaleModel
from app.domain.sale import PaymentMethod, Sale
from app.domain.shared import normalize_money


@dataclass(frozen=True, slots=True)
class SaleSessionMetrics:
    sales_amount: Decimal
    sales_count: int
    average_ticket_amount: Decimal
    total_received_amount: Decimal
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


class SaleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, sale: Sale) -> Sale:
        sale_model = SaleModel.from_domain(sale)
        self.db.add(sale_model)
        self.db.flush()
        self.db.refresh(sale_model)

        item_models = [SaleItemModel.from_domain(item, sale.id) for item in sale.items]
        self.db.add_all(item_models)
        self.db.flush()

        items = tuple(item_model.to_domain() for item_model in item_models)
        return sale_model.to_domain(items)

    def get_total_sales_amount_for_session(self, session_id: UUID) -> float:
        statement = select(func.coalesce(func.sum(SaleModel.total_amount), 0)).where(
            SaleModel.cash_register_session_id == str(session_id),
        )
        return float(self.db.scalar(statement) or 0)

    def get_session_metrics(self, session_id: UUID) -> SaleSessionMetrics:
        statement = select(
            func.coalesce(func.sum(SaleModel.total_amount), 0),
            func.count(SaleModel.id),
            func.max(SaleModel.created_at),
            func.coalesce(
                func.sum(
                    case(
                        (
                            SaleModel.payment_method == PaymentMethod.CASH.value,
                            SaleModel.total_amount,
                        ),
                        else_=0,
                    ),
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            SaleModel.payment_method == PaymentMethod.PIX.value,
                            SaleModel.total_amount,
                        ),
                        else_=0,
                    ),
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            SaleModel.payment_method == PaymentMethod.DEBIT_CARD.value,
                            SaleModel.total_amount,
                        ),
                        else_=0,
                    ),
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            SaleModel.payment_method == PaymentMethod.CREDIT_CARD.value,
                            SaleModel.total_amount,
                        ),
                        else_=0,
                    ),
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            SaleModel.payment_method == PaymentMethod.MIXED.value,
                            SaleModel.total_amount,
                        ),
                        else_=0,
                    ),
                ),
                0,
            ),
            func.coalesce(func.sum(SaleModel.cash_amount), 0),
            func.coalesce(func.sum(SaleModel.pix_amount), 0),
            func.coalesce(func.sum(SaleModel.debit_card_amount), 0),
            func.coalesce(func.sum(SaleModel.credit_card_amount), 0),
        ).where(SaleModel.cash_register_session_id == str(session_id))

        (
            sales_amount_raw,
            sales_count_raw,
            last_sale_at,
            cash_sales_amount_raw,
            pix_sales_amount_raw,
            debit_card_sales_amount_raw,
            credit_card_sales_amount_raw,
            mixed_sales_amount_raw,
            cash_received_amount_raw,
            pix_received_amount_raw,
            debit_card_received_amount_raw,
            credit_card_received_amount_raw,
        ) = self.db.execute(statement).one()
        sales_amount = normalize_money(Decimal(str(sales_amount_raw or 0)))
        sales_count = int(sales_count_raw or 0)
        average_ticket_amount = (
            normalize_money(sales_amount / sales_count) if sales_count > 0 else Decimal("0.00")
        )

        return SaleSessionMetrics(
            sales_amount=sales_amount,
            sales_count=sales_count,
            average_ticket_amount=average_ticket_amount,
            total_received_amount=sales_amount,
            cash_sales_amount=normalize_money(Decimal(str(cash_sales_amount_raw or 0))),
            pix_sales_amount=normalize_money(Decimal(str(pix_sales_amount_raw or 0))),
            debit_card_sales_amount=normalize_money(Decimal(str(debit_card_sales_amount_raw or 0))),
            credit_card_sales_amount=normalize_money(
                Decimal(str(credit_card_sales_amount_raw or 0))
            ),
            mixed_sales_amount=normalize_money(Decimal(str(mixed_sales_amount_raw or 0))),
            cash_received_amount=normalize_money(Decimal(str(cash_received_amount_raw or 0))),
            pix_received_amount=normalize_money(Decimal(str(pix_received_amount_raw or 0))),
            debit_card_received_amount=normalize_money(
                Decimal(str(debit_card_received_amount_raw or 0))
            ),
            credit_card_received_amount=normalize_money(
                Decimal(str(credit_card_received_amount_raw or 0))
            ),
            last_sale_at=last_sale_at,
        )
