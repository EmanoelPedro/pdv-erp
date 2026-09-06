from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.domain.expense import ExpenseCategory
from app.domain.sale import PaymentMethod
from app.domain.shared import normalize_money
from app.repositories.report_repository import ReportFilters, ReportRepository
from app.services.cash_register_service import CashRegisterService, CashRegisterSessionSnapshot


@dataclass(frozen=True, slots=True)
class SalesSummaryRow:
    report_date: date
    sales_count: int
    gross_sales: Decimal
    discounts: Decimal
    final_sales: Decimal
    expenses: Decimal
    estimated_result: Decimal


@dataclass(frozen=True, slots=True)
class ProductPerformanceRow:
    product_id: UUID
    product_name: str
    quantity_sold: int
    revenue: Decimal
    average_sale_participation: Decimal


@dataclass(frozen=True, slots=True)
class CategoryPerformanceRow:
    category_id: UUID
    category_name: str
    revenue: Decimal
    units_sold: int
    percentage_of_total: Decimal


@dataclass(frozen=True, slots=True)
class PaymentMethodReportRow:
    payment_method: PaymentMethod
    transactions: int
    revenue: Decimal
    percentage_of_total: Decimal


@dataclass(frozen=True, slots=True)
class HourlySalesRow:
    hour: str
    sales_count: int
    revenue: Decimal


@dataclass(frozen=True, slots=True)
class ExpenseAnalysisRow:
    category: ExpenseCategory
    amount: Decimal
    count: int
    percentage_of_total: Decimal


class ReportService:
    def __init__(
        self,
        report_repository: ReportRepository,
        cash_register_service: CashRegisterService,
    ) -> None:
        self.report_repository = report_repository
        self.cash_register_service = cash_register_service

    def list_sales_summary(self, filters: ReportFilters) -> list[SalesSummaryRow]:
        sales_rows = self.report_repository.get_sales_summary_rows(filters)
        expense_rows = self.report_repository.get_daily_expenses_rows(filters)
        expenses_by_date = {
            date.fromisoformat(str(row["report_date"])): self._money(row["expenses_amount"])
            for row in expense_rows
            if row["report_date"] is not None
        }

        summary_rows: list[SalesSummaryRow] = []
        for row in sales_rows:
            report_date = date.fromisoformat(str(row["report_date"]))
            gross_sales = self._money(row["gross_sales"])
            expenses = expenses_by_date.get(report_date, Decimal("0.00"))
            discounts = Decimal("0.00")
            final_sales = gross_sales
            summary_rows.append(
                SalesSummaryRow(
                    report_date=report_date,
                    sales_count=int(row["sales_count"] or 0),
                    gross_sales=gross_sales,
                    discounts=discounts,
                    final_sales=final_sales,
                    expenses=expenses,
                    estimated_result=normalize_money(final_sales - expenses),
                ),
            )

        return summary_rows

    def list_product_performance(self, filters: ReportFilters) -> list[ProductPerformanceRow]:
        rows = self.report_repository.get_product_performance_rows(filters)
        sales_count = int(self.report_repository.get_sales_overview(filters)["sales_count"] or 0)

        return [
            ProductPerformanceRow(
                product_id=UUID(str(row["product_id"])),
                product_name=str(row["product_name"]),
                quantity_sold=int(row["quantity_sold"] or 0),
                revenue=self._money(row["revenue"]),
                average_sale_participation=self._percentage(
                    int(row["sales_with_product"] or 0),
                    sales_count,
                ),
            )
            for row in rows
        ]

    def list_category_performance(self, filters: ReportFilters) -> list[CategoryPerformanceRow]:
        rows = self.report_repository.get_category_performance_rows(filters)
        total_revenue = sum((self._money(row["revenue"]) for row in rows), start=Decimal("0.00"))

        return [
            CategoryPerformanceRow(
                category_id=UUID(str(row["category_id"])),
                category_name=str(row["category_name"]),
                revenue=self._money(row["revenue"]),
                units_sold=int(row["units_sold"] or 0),
                percentage_of_total=self._percentage(self._money(row["revenue"]), total_revenue),
            )
            for row in rows
        ]

    def list_payment_methods(self, filters: ReportFilters) -> list[PaymentMethodReportRow]:
        rows = self.report_repository.get_payment_method_rows(filters)
        total_revenue = sum((self._money(row["revenue"]) for row in rows), start=Decimal("0.00"))

        return [
            PaymentMethodReportRow(
                payment_method=PaymentMethod(str(row["payment_method"])),
                transactions=int(row["transactions"] or 0),
                revenue=self._money(row["revenue"]),
                percentage_of_total=self._percentage(self._money(row["revenue"]), total_revenue),
            )
            for row in rows
        ]

    def list_hourly_sales(self, filters: ReportFilters) -> list[HourlySalesRow]:
        rows = self.report_repository.get_hourly_sales(filters)
        return [
            HourlySalesRow(
                hour=str(row["hour"]),
                sales_count=int(row["sales_count"] or 0),
                revenue=self._money(row["revenue"]),
            )
            for row in rows
        ]

    def list_cash_register_sessions(
        self, filters: ReportFilters
    ) -> list[CashRegisterSessionSnapshot]:
        snapshots = self.cash_register_service.list_session_snapshots(
            start_date=filters.start_date,
            end_date=filters.end_date,
        )
        if filters.cash_register_session_id is not None:
            return [
                snapshot
                for snapshot in snapshots
                if snapshot.session.id == filters.cash_register_session_id
            ]
        return snapshots

    def list_expense_analysis(self, filters: ReportFilters) -> list[ExpenseAnalysisRow]:
        rows = self.report_repository.get_expense_analysis_rows(filters)
        total_amount = sum((self._money(row["amount"]) for row in rows), start=Decimal("0.00"))

        return [
            ExpenseAnalysisRow(
                category=ExpenseCategory(str(row["category"])),
                amount=self._money(row["amount"]),
                count=int(row["count"] or 0),
                percentage_of_total=self._percentage(self._money(row["amount"]), total_amount),
            )
            for row in rows
        ]

    def _money(self, value: object) -> Decimal:
        return normalize_money(Decimal(str(value or 0)))

    def _percentage(self, value: Decimal | int, total: Decimal | int) -> Decimal:
        normalized_total = Decimal(str(total or 0))
        if normalized_total == 0:
            return Decimal("0.00")
        normalized_value = Decimal(str(value or 0))
        return normalize_money((normalized_value / normalized_total) * Decimal("100.00"))
