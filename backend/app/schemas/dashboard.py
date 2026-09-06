from dataclasses import asdict
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.services.dashboard_service import (
    DashboardCategoryHighlight,
    DashboardDailyRevenuePoint,
    DashboardHourlyPoint,
    DashboardProductHighlight,
    DashboardSummary,
)


class DashboardProductHighlightResponse(BaseModel):
    product_id: UUID
    product_name: str
    quantity_sold: int
    revenue: Decimal

    @classmethod
    def from_service(cls, value: DashboardProductHighlight) -> "DashboardProductHighlightResponse":
        return cls(**asdict(value))


class DashboardCategoryHighlightResponse(BaseModel):
    category_id: UUID
    category_name: str
    revenue: Decimal
    units_sold: int

    @classmethod
    def from_service(
        cls, value: DashboardCategoryHighlight
    ) -> "DashboardCategoryHighlightResponse":
        return cls(**asdict(value))


class DashboardHourlyPointResponse(BaseModel):
    hour: str
    sales_count: int
    revenue: Decimal

    @classmethod
    def from_service(cls, value: DashboardHourlyPoint) -> "DashboardHourlyPointResponse":
        return cls(**asdict(value))


class DashboardDailyRevenuePointResponse(BaseModel):
    report_date: date
    revenue: Decimal

    @classmethod
    def from_service(
        cls, value: DashboardDailyRevenuePoint
    ) -> "DashboardDailyRevenuePointResponse":
        return cls(**asdict(value))


class DashboardSummaryResponse(BaseModel):
    report_date: date
    revenue_today: Decimal
    expenses_today: Decimal
    profit_estimate_today: Decimal
    average_ticket_today: Decimal
    sales_count_today: int
    latest_cash_difference: Decimal | None
    latest_cash_difference_at: date | None
    best_selling_product_today: DashboardProductHighlightResponse | None
    best_category_today: DashboardCategoryHighlightResponse | None
    sales_by_hour_today: list[DashboardHourlyPointResponse]
    revenue_last_7_days: list[DashboardDailyRevenuePointResponse]

    @classmethod
    def from_service(cls, value: DashboardSummary) -> "DashboardSummaryResponse":
        return cls(
            report_date=value.report_date,
            revenue_today=value.revenue_today,
            expenses_today=value.expenses_today,
            profit_estimate_today=value.profit_estimate_today,
            average_ticket_today=value.average_ticket_today,
            sales_count_today=value.sales_count_today,
            latest_cash_difference=value.latest_cash_difference,
            latest_cash_difference_at=value.latest_cash_difference_at,
            best_selling_product_today=(
                DashboardProductHighlightResponse.from_service(value.best_selling_product_today)
                if value.best_selling_product_today is not None
                else None
            ),
            best_category_today=(
                DashboardCategoryHighlightResponse.from_service(value.best_category_today)
                if value.best_category_today is not None
                else None
            ),
            sales_by_hour_today=[
                DashboardHourlyPointResponse.from_service(point)
                for point in value.sales_by_hour_today
            ],
            revenue_last_7_days=[
                DashboardDailyRevenuePointResponse.from_service(point)
                for point in value.revenue_last_7_days
            ],
        )
