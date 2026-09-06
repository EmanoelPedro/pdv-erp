from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from app.domain.shared import normalize_money, utc_now
from app.repositories.report_repository import ReportFilters, ReportRepository


@dataclass(frozen=True, slots=True)
class DashboardProductHighlight:
    product_id: UUID
    product_name: str
    quantity_sold: int
    revenue: Decimal


@dataclass(frozen=True, slots=True)
class DashboardCategoryHighlight:
    category_id: UUID
    category_name: str
    revenue: Decimal
    units_sold: int


@dataclass(frozen=True, slots=True)
class DashboardHourlyPoint:
    hour: str
    sales_count: int
    revenue: Decimal


@dataclass(frozen=True, slots=True)
class DashboardDailyRevenuePoint:
    report_date: date
    revenue: Decimal


@dataclass(frozen=True, slots=True)
class DashboardSummary:
    report_date: date
    revenue_today: Decimal
    expenses_today: Decimal
    profit_estimate_today: Decimal
    average_ticket_today: Decimal
    sales_count_today: int
    latest_cash_difference: Decimal | None
    latest_cash_difference_at: date | None
    best_selling_product_today: DashboardProductHighlight | None
    best_category_today: DashboardCategoryHighlight | None
    sales_by_hour_today: list[DashboardHourlyPoint]
    revenue_last_7_days: list[DashboardDailyRevenuePoint]


class DashboardService:
    def __init__(self, report_repository: ReportRepository) -> None:
        self.report_repository = report_repository

    def get_today_summary(self) -> DashboardSummary:
        today = utc_now().date()
        today_filters = ReportFilters(start_date=today, end_date=today)
        last_week_filters = ReportFilters(start_date=today - timedelta(days=6), end_date=today)

        sales_overview = self.report_repository.get_sales_overview(today_filters)
        expenses_overview = self.report_repository.get_expenses_overview(today_filters)
        best_product_raw = self.report_repository.get_best_selling_product(today_filters)
        best_category_raw = self.report_repository.get_top_category_by_revenue(today_filters)
        hourly_rows = self.report_repository.get_hourly_sales(today_filters)
        trend_rows = self.report_repository.get_revenue_by_day(last_week_filters)
        latest_cash_difference_raw = self.report_repository.get_latest_closed_cash_difference()

        revenue_today = self._money(sales_overview["sales_amount"])
        expenses_today = self._money(expenses_overview["expenses_amount"])
        sales_count_today = int(sales_overview["sales_count"] or 0)
        average_ticket_today = (
            normalize_money(revenue_today / sales_count_today)
            if sales_count_today > 0
            else Decimal("0.00")
        )

        return DashboardSummary(
            report_date=today,
            revenue_today=revenue_today,
            expenses_today=expenses_today,
            profit_estimate_today=normalize_money(revenue_today - expenses_today),
            average_ticket_today=average_ticket_today,
            sales_count_today=sales_count_today,
            latest_cash_difference=(
                self._money(latest_cash_difference_raw["difference_amount"])
                if latest_cash_difference_raw is not None
                else None
            ),
            latest_cash_difference_at=(
                latest_cash_difference_raw["closed_at"].date()
                if latest_cash_difference_raw is not None
                and latest_cash_difference_raw["closed_at"] is not None
                else None
            ),
            best_selling_product_today=self._map_best_product(best_product_raw),
            best_category_today=self._map_best_category(best_category_raw),
            sales_by_hour_today=self._build_hourly_points(hourly_rows),
            revenue_last_7_days=self._build_daily_points(today, trend_rows),
        )

    def _map_best_product(self, row: dict[str, object] | None) -> DashboardProductHighlight | None:
        if row is None:
            return None
        return DashboardProductHighlight(
            product_id=UUID(str(row["product_id"])),
            product_name=str(row["product_name"]),
            quantity_sold=int(row["quantity_sold"] or 0),
            revenue=self._money(row["revenue"]),
        )

    def _map_best_category(
        self, row: dict[str, object] | None
    ) -> DashboardCategoryHighlight | None:
        if row is None:
            return None
        return DashboardCategoryHighlight(
            category_id=UUID(str(row["category_id"])),
            category_name=str(row["category_name"]),
            revenue=self._money(row["revenue"]),
            units_sold=int(row["units_sold"] or 0),
        )

    def _build_hourly_points(self, rows: list[dict[str, object]]) -> list[DashboardHourlyPoint]:
        row_map = {str(row["hour"]): row for row in rows}
        points: list[DashboardHourlyPoint] = []
        for hour in range(24):
            label = f"{hour:02d}:00"
            row = row_map.get(label)
            points.append(
                DashboardHourlyPoint(
                    hour=label,
                    sales_count=int(row["sales_count"] or 0) if row else 0,
                    revenue=self._money(row["revenue"]) if row else Decimal("0.00"),
                ),
            )
        return points

    def _build_daily_points(
        self,
        today: date,
        rows: list[dict[str, object]],
    ) -> list[DashboardDailyRevenuePoint]:
        row_map = {
            date.fromisoformat(str(row["report_date"])): self._money(row["revenue"])
            for row in rows
            if row["report_date"] is not None
        }
        return [
            DashboardDailyRevenuePoint(
                report_date=day,
                revenue=row_map.get(day, Decimal("0.00")),
            )
            for day in [today - timedelta(days=offset) for offset in range(6, -1, -1)]
        ]

    def _money(self, value: object) -> Decimal:
        return normalize_money(Decimal(str(value or 0)))
