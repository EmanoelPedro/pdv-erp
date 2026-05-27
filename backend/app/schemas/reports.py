from dataclasses import asdict
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.expense import ExpenseCategory
from app.domain.sale import PaymentMethod
from app.schemas.cash_register import CashRegisterSessionResponse
from app.services.report_service import (
    CategoryPerformanceRow,
    ExpenseAnalysisRow,
    HourlySalesRow,
    PaymentMethodReportRow,
    ProductPerformanceRow,
    SalesSummaryRow,
)


class ReportFiltersQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    category_id: UUID | None = None
    payment_method: PaymentMethod | None = None
    user_id: UUID | None = None
    cash_register_session_id: UUID | None = None


class SalesSummaryRowResponse(BaseModel):
    report_date: date
    sales_count: int
    gross_sales: Decimal
    discounts: Decimal
    final_sales: Decimal
    expenses: Decimal
    estimated_result: Decimal

    @classmethod
    def from_service(cls, value: SalesSummaryRow) -> "SalesSummaryRowResponse":
        return cls(**asdict(value))


class ProductPerformanceRowResponse(BaseModel):
    product_id: UUID
    product_name: str
    quantity_sold: int
    revenue: Decimal
    average_sale_participation: Decimal = Field(
        description="Percent of filtered sales containing the product.")

    @classmethod
    def from_service(cls, value: ProductPerformanceRow) -> "ProductPerformanceRowResponse":
        return cls(**asdict(value))


class CategoryPerformanceRowResponse(BaseModel):
    category_id: UUID
    category_name: str
    revenue: Decimal
    units_sold: int
    percentage_of_total: Decimal

    @classmethod
    def from_service(cls, value: CategoryPerformanceRow) -> "CategoryPerformanceRowResponse":
        return cls(**asdict(value))


class PaymentMethodReportRowResponse(BaseModel):
    payment_method: PaymentMethod
    transactions: int
    revenue: Decimal
    percentage_of_total: Decimal

    @classmethod
    def from_service(cls, value: PaymentMethodReportRow) -> "PaymentMethodReportRowResponse":
        return cls(**asdict(value))


class HourlySalesRowResponse(BaseModel):
    hour: str
    sales_count: int
    revenue: Decimal

    @classmethod
    def from_service(cls, value: HourlySalesRow) -> "HourlySalesRowResponse":
        return cls(**asdict(value))


class ExpenseAnalysisRowResponse(BaseModel):
    category: ExpenseCategory
    amount: Decimal
    count: int
    percentage_of_total: Decimal

    @classmethod
    def from_service(cls, value: ExpenseAnalysisRow) -> "ExpenseAnalysisRowResponse":
        return cls(**asdict(value))
