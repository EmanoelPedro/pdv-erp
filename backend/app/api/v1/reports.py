from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_owner_user, get_report_service
from app.domain.user import User
from app.repositories.report_repository import ReportFilters
from app.schemas.cash_register import CashRegisterSessionResponse
from app.schemas.reports import (
    CategoryPerformanceRowResponse,
    ExpenseAnalysisRowResponse,
    HourlySalesRowResponse,
    PaymentMethodReportRowResponse,
    ProductPerformanceRowResponse,
    ReportFiltersQuery,
    SalesSummaryRowResponse,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def _to_filters(query: ReportFiltersQuery) -> ReportFilters:
    return ReportFilters(
        start_date=query.start_date,
        end_date=query.end_date,
        category_id=query.category_id,
        payment_method=query.payment_method,
        user_id=query.user_id,
        cash_register_session_id=query.cash_register_session_id,
    )


@router.get("/sales", response_model=list[SalesSummaryRowResponse])
def get_sales_summary_report(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[ReportFiltersQuery, Depends()],
) -> list[SalesSummaryRowResponse]:
    return [
        SalesSummaryRowResponse.from_service(row)
        for row in service.list_sales_summary(_to_filters(query))
    ]


@router.get("/products", response_model=list[ProductPerformanceRowResponse])
def get_product_performance_report(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[ReportFiltersQuery, Depends()],
) -> list[ProductPerformanceRowResponse]:
    return [
        ProductPerformanceRowResponse.from_service(row)
        for row in service.list_product_performance(_to_filters(query))
    ]


@router.get("/categories", response_model=list[CategoryPerformanceRowResponse])
def get_category_performance_report(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[ReportFiltersQuery, Depends()],
) -> list[CategoryPerformanceRowResponse]:
    return [
        CategoryPerformanceRowResponse.from_service(row)
        for row in service.list_category_performance(_to_filters(query))
    ]


@router.get("/payments", response_model=list[PaymentMethodReportRowResponse])
def get_payment_method_report(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[ReportFiltersQuery, Depends()],
) -> list[PaymentMethodReportRowResponse]:
    return [
        PaymentMethodReportRowResponse.from_service(row)
        for row in service.list_payment_methods(_to_filters(query))
    ]


@router.get("/hourly-sales", response_model=list[HourlySalesRowResponse])
def get_hourly_sales_report(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[ReportFiltersQuery, Depends()],
) -> list[HourlySalesRowResponse]:
    return [
        HourlySalesRowResponse.from_service(row)
        for row in service.list_hourly_sales(_to_filters(query))
    ]


@router.get("/cash-registers", response_model=list[CashRegisterSessionResponse])
def get_cash_register_report(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[ReportFiltersQuery, Depends()],
) -> list[CashRegisterSessionResponse]:
    return [
        CashRegisterSessionResponse.from_domain(
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
        )
        for snapshot in service.list_cash_register_sessions(_to_filters(query))
    ]


@router.get("/expenses", response_model=list[ExpenseAnalysisRowResponse])
def get_expense_analysis_report(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[ReportFiltersQuery, Depends()],
) -> list[ExpenseAnalysisRowResponse]:
    return [
        ExpenseAnalysisRowResponse.from_service(row)
        for row in service.list_expense_analysis(_to_filters(query))
    ]
