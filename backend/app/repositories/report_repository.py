from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.database.models import (
    CashRegisterSessionModel,
    CategoryModel,
    ExpenseModel,
    ProductModel,
    SaleItemModel,
    SaleModel,
)
from app.domain.cash_register import CashRegisterStatus
from app.domain.expense import ExpenseCategory
from app.domain.sale import PaymentMethod, SaleStatus


@dataclass(frozen=True, slots=True)
class ReportFilters:
    start_date: date | None = None
    end_date: date | None = None
    category_id: UUID | None = None
    payment_method: PaymentMethod | None = None
    user_id: UUID | None = None
    cash_register_session_id: UUID | None = None


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_sales_overview(self, filters: ReportFilters) -> dict[str, object]:
        statement = select(
            func.coalesce(func.sum(SaleModel.total_amount),
                          0).label("sales_amount"),
            func.count(SaleModel.id).label("sales_count"),
        ).select_from(SaleModel)
        statement = self._apply_sale_filters(statement, filters)
        return dict(self.db.execute(statement).mappings().one())

    def get_expenses_overview(self, filters: ReportFilters) -> dict[str, object]:
        statement = select(
            func.coalesce(func.sum(ExpenseModel.amount),
                          0).label("expenses_amount"),
            func.count(ExpenseModel.id).label("expenses_count"),
        ).select_from(ExpenseModel)
        statement = self._apply_expense_filters(statement, filters)
        return dict(self.db.execute(statement).mappings().one())

    def get_latest_closed_cash_difference(self) -> dict[str, object] | None:
        statement = (
            select(
                CashRegisterSessionModel.id.label("session_id"),
                CashRegisterSessionModel.difference_amount.label(
                    "difference_amount"),
                CashRegisterSessionModel.closed_at.label("closed_at"),
            )
            .where(CashRegisterSessionModel.status == CashRegisterStatus.CLOSED.value)
            .order_by(CashRegisterSessionModel.closed_at.desc())
            .limit(1)
        )
        row = self.db.execute(statement).mappings().first()
        return dict(row) if row else None

    def get_best_selling_product(self, filters: ReportFilters) -> dict[str, object] | None:
        statement = (
            select(
                ProductModel.id.label("product_id"),
                ProductModel.name.label("product_name"),
                func.sum(SaleItemModel.quantity).label("quantity_sold"),
                func.coalesce(func.sum(SaleItemModel.total_price),
                              0).label("revenue"),
            )
            .select_from(SaleItemModel)
            .join(SaleModel, SaleModel.id == SaleItemModel.sale_id)
            .join(ProductModel, ProductModel.id == SaleItemModel.product_id)
            .group_by(ProductModel.id, ProductModel.name)
            .order_by(func.sum(SaleItemModel.quantity).desc(), func.sum(SaleItemModel.total_price).desc())
            .limit(1)
        )
        statement = self._apply_item_sale_filters(statement, filters)
        row = self.db.execute(statement).mappings().first()
        return dict(row) if row else None

    def get_top_category_by_revenue(self, filters: ReportFilters) -> dict[str, object] | None:
        statement = (
            select(
                CategoryModel.id.label("category_id"),
                CategoryModel.name.label("category_name"),
                func.coalesce(func.sum(SaleItemModel.total_price),
                              0).label("revenue"),
                func.coalesce(func.sum(SaleItemModel.quantity),
                              0).label("units_sold"),
            )
            .select_from(SaleItemModel)
            .join(SaleModel, SaleModel.id == SaleItemModel.sale_id)
            .join(ProductModel, ProductModel.id == SaleItemModel.product_id)
            .join(CategoryModel, CategoryModel.id == ProductModel.category_id)
            .group_by(CategoryModel.id, CategoryModel.name)
            .order_by(func.sum(SaleItemModel.total_price).desc(), func.sum(SaleItemModel.quantity).desc())
            .limit(1)
        )
        statement = self._apply_item_sale_filters(statement, filters)
        row = self.db.execute(statement).mappings().first()
        return dict(row) if row else None

    def get_revenue_by_day(self, filters: ReportFilters) -> list[dict[str, object]]:
        statement = (
            select(
                func.date(SaleModel.created_at).label("report_date"),
                func.coalesce(func.sum(SaleModel.total_amount),
                              0).label("revenue"),
            )
            .select_from(SaleModel)
            .group_by(func.date(SaleModel.created_at))
            .order_by(func.date(SaleModel.created_at).asc())
        )
        statement = self._apply_sale_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def get_hourly_sales(self, filters: ReportFilters) -> list[dict[str, object]]:
        hour_label = func.strftime("%H:00", SaleModel.created_at)
        statement = (
            select(
                hour_label.label("hour"),
                func.count(SaleModel.id).label("sales_count"),
                func.coalesce(func.sum(SaleModel.total_amount),
                              0).label("revenue"),
            )
            .select_from(SaleModel)
            .group_by(hour_label)
            .order_by(hour_label.asc())
        )
        statement = self._apply_sale_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def get_sales_summary_rows(self, filters: ReportFilters) -> list[dict[str, object]]:
        report_date = func.date(SaleModel.created_at)
        statement = (
            select(
                report_date.label("report_date"),
                func.count(SaleModel.id).label("sales_count"),
                func.coalesce(func.sum(SaleModel.total_amount),
                              0).label("gross_sales"),
            )
            .select_from(SaleModel)
            .group_by(report_date)
            .order_by(report_date.desc())
        )
        statement = self._apply_sale_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def get_daily_expenses_rows(self, filters: ReportFilters) -> list[dict[str, object]]:
        report_date = func.date(ExpenseModel.expense_date)
        statement = (
            select(
                report_date.label("report_date"),
                func.coalesce(func.sum(ExpenseModel.amount),
                              0).label("expenses_amount"),
            )
            .select_from(ExpenseModel)
            .group_by(report_date)
            .order_by(report_date.desc())
        )
        statement = self._apply_expense_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def get_product_performance_rows(self, filters: ReportFilters) -> list[dict[str, object]]:
        statement = (
            select(
                ProductModel.id.label("product_id"),
                ProductModel.name.label("product_name"),
                func.coalesce(func.sum(SaleItemModel.quantity),
                              0).label("quantity_sold"),
                func.coalesce(func.sum(SaleItemModel.total_price),
                              0).label("revenue"),
                func.count(func.distinct(SaleModel.id)).label(
                    "sales_with_product"),
            )
            .select_from(SaleItemModel)
            .join(SaleModel, SaleModel.id == SaleItemModel.sale_id)
            .join(ProductModel, ProductModel.id == SaleItemModel.product_id)
            .group_by(ProductModel.id, ProductModel.name)
            .order_by(func.sum(SaleItemModel.quantity).desc(), func.sum(SaleItemModel.total_price).desc())
        )
        statement = self._apply_item_sale_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def get_category_performance_rows(self, filters: ReportFilters) -> list[dict[str, object]]:
        statement = (
            select(
                CategoryModel.id.label("category_id"),
                CategoryModel.name.label("category_name"),
                func.coalesce(func.sum(SaleItemModel.total_price),
                              0).label("revenue"),
                func.coalesce(func.sum(SaleItemModel.quantity),
                              0).label("units_sold"),
            )
            .select_from(SaleItemModel)
            .join(SaleModel, SaleModel.id == SaleItemModel.sale_id)
            .join(ProductModel, ProductModel.id == SaleItemModel.product_id)
            .join(CategoryModel, CategoryModel.id == ProductModel.category_id)
            .group_by(CategoryModel.id, CategoryModel.name)
            .order_by(func.sum(SaleItemModel.total_price).desc(), func.sum(SaleItemModel.quantity).desc())
        )
        statement = self._apply_item_sale_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def get_payment_method_rows(self, filters: ReportFilters) -> list[dict[str, object]]:
        statement = (
            select(
                SaleModel.payment_method.label("payment_method"),
                func.count(SaleModel.id).label("transactions"),
                func.coalesce(func.sum(SaleModel.total_amount),
                              0).label("revenue"),
            )
            .select_from(SaleModel)
            .group_by(SaleModel.payment_method)
            .order_by(func.sum(SaleModel.total_amount).desc())
        )
        statement = self._apply_sale_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def get_expense_analysis_rows(self, filters: ReportFilters) -> list[dict[str, object]]:
        statement = (
            select(
                ExpenseModel.category.label("category"),
                func.count(ExpenseModel.id).label("count"),
                func.coalesce(func.sum(ExpenseModel.amount),
                              0).label("amount"),
            )
            .select_from(ExpenseModel)
            .group_by(ExpenseModel.category)
            .order_by(func.sum(ExpenseModel.amount).desc())
        )
        statement = self._apply_expense_filters(statement, filters)
        return [dict(row) for row in self.db.execute(statement).mappings().all()]

    def _apply_sale_filters(self, statement: Select[tuple], filters: ReportFilters) -> Select[tuple]:
        statement = statement.where(
            SaleModel.status == SaleStatus.COMPLETED.value)
        statement = self._apply_date_range(
            statement, SaleModel.created_at, filters.start_date, filters.end_date)

        if filters.payment_method is not None:
            statement = statement.where(
                SaleModel.payment_method == filters.payment_method.value)
        if filters.user_id is not None:
            statement = statement.where(
                SaleModel.seller_user_id == str(filters.user_id))
        if filters.cash_register_session_id is not None:
            statement = statement.where(
                SaleModel.cash_register_session_id == str(filters.cash_register_session_id))
        if filters.category_id is not None:
            category_sales = (
                select(SaleItemModel.sale_id)
                .join(ProductModel, ProductModel.id == SaleItemModel.product_id)
                .where(ProductModel.category_id == str(filters.category_id))
            )
            statement = statement.where(SaleModel.id.in_(category_sales))

        return statement

    def _apply_item_sale_filters(self, statement: Select[tuple], filters: ReportFilters) -> Select[tuple]:
        statement = statement.where(
            SaleModel.status == SaleStatus.COMPLETED.value)
        statement = self._apply_date_range(
            statement, SaleModel.created_at, filters.start_date, filters.end_date)

        if filters.payment_method is not None:
            statement = statement.where(
                SaleModel.payment_method == filters.payment_method.value)
        if filters.user_id is not None:
            statement = statement.where(
                SaleModel.seller_user_id == str(filters.user_id))
        if filters.cash_register_session_id is not None:
            statement = statement.where(
                SaleModel.cash_register_session_id == str(filters.cash_register_session_id))
        if filters.category_id is not None:
            statement = statement.where(
                ProductModel.category_id == str(filters.category_id))

        return statement

    def _apply_expense_filters(self, statement: Select[tuple], filters: ReportFilters) -> Select[tuple]:
        statement = self._apply_date_range(
            statement, ExpenseModel.expense_date, filters.start_date, filters.end_date)

        if filters.payment_method is not None:
            statement = statement.where(
                ExpenseModel.payment_method == filters.payment_method.value)
        if filters.user_id is not None:
            statement = statement.where(
                ExpenseModel.created_by_user_id == str(filters.user_id))
        if filters.cash_register_session_id is not None:
            statement = statement.where(
                ExpenseModel.cash_register_session_id == str(filters.cash_register_session_id))

        return statement

    def _apply_date_range(
        self,
        statement: Select[tuple],
        column,
        start_date: date | None,
        end_date: date | None,
    ) -> Select[tuple]:
        if start_date is not None:
            started_at = datetime.combine(start_date, time.min, tzinfo=UTC)
            statement = statement.where(column >= started_at)
        if end_date is not None:
            ended_at = datetime.combine(
                end_date + timedelta(days=1), time.min, tzinfo=UTC)
            statement = statement.where(column < ended_at)
        return statement
