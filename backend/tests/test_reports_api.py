from datetime import UTC, datetime, time, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.domain.catalog import Category, Product
from app.domain.cash_register import CashRegisterSession
from app.domain.expense import Expense, ExpenseCategory
from app.domain.sale import PaymentBreakdown, PaymentMethod, Sale, SaleItem
from app.domain.shared import utc_now
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.catalog_repository import CategoryRepository, ProductRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.user_repository import UserRepository


def _at(hour: int, minute: int = 0) -> datetime:
    today = utc_now().date()
    return datetime.combine(today, time(hour=hour, minute=minute), tzinfo=UTC)


def _seed_owner_report_data(db_session: Session) -> None:
    owner = UserRepository(db_session).get_by_username("owner")
    assert owner is not None

    category = CategoryRepository(db_session).create(
        Category.create(name="Salgados", created_at=_at(7)))
    product = ProductRepository(db_session).create(
        Product.create(
            category_id=category.id,
            name="Pastel",
            price=Decimal("14.00"),
            created_at=_at(7),
        ),
    )
    cash_session_repository = CashRegisterSessionRepository(db_session)
    session = cash_session_repository.create(
        CashRegisterSession.open(Decimal("200.00"), opened_at=_at(8)))

    sale_item = SaleItem.from_product(product, quantity=2, created_at=_at(9))
    sale = Sale.create(
        cash_register_session_id=session.id,
        seller_user_id=owner.id,
        items=(sale_item,),
        payment=PaymentBreakdown.create(
            PaymentMethod.CASH, sale_item.total_price),
        created_at=_at(9),
    )
    SaleRepository(db_session).create(sale)
    ExpenseRepository(db_session).create(
        Expense.create(
            description="Compra de massa",
            amount=Decimal("10.00"),
            category=ExpenseCategory.INGREDIENTS,
            payment_method=PaymentMethod.CASH,
            created_by_user_id=owner.id,
            cash_register_session_id=session.id,
            expense_date=_at(10),
            created_at=_at(10),
        ),
    )
    cash_session_repository.update(session.close(
        Decimal("210.00"), closed_at=_at(18)))
    db_session.commit()


def test_reports_endpoints_require_owner_role(
    client: TestClient,
    owner_auth_headers: dict[str, str],
    employee_auth_headers: dict[str, str],
) -> None:
    dashboard_response = client.get(
        "/api/v1/dashboard/summary", headers=employee_auth_headers)
    sales_report_response = client.get(
        "/api/v1/reports/sales", headers=employee_auth_headers)

    assert dashboard_response.status_code == 403
    assert sales_report_response.status_code == 403


def test_owner_can_read_dashboard_and_reports(
    client: TestClient,
    db_session: Session,
    owner_auth_headers: dict[str, str],
) -> None:
    _seed_owner_report_data(db_session)
    today = utc_now().date().isoformat()

    dashboard_response = client.get(
        "/api/v1/dashboard/summary", headers=owner_auth_headers)
    sales_report_response = client.get(
        f"/api/v1/reports/sales?start_date={today}&end_date={today}",
        headers=owner_auth_headers,
    )
    payments_report_response = client.get(
        f"/api/v1/reports/payments?start_date={today}&end_date={today}",
        headers=owner_auth_headers,
    )
    cash_register_report_response = client.get(
        f"/api/v1/reports/cash-registers?start_date={today}&end_date={today}",
        headers=owner_auth_headers,
    )
    expenses_report_response = client.get(
        f"/api/v1/reports/expenses?start_date={today}&end_date={today}",
        headers=owner_auth_headers,
    )

    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["revenue_today"] == "28.00"
    assert dashboard_response.json()["expenses_today"] == "10.00"
    assert dashboard_response.json()["sales_count_today"] == 1

    assert sales_report_response.status_code == 200
    assert sales_report_response.json()[0]["gross_sales"] == "28.00"
    assert sales_report_response.json()[0]["estimated_result"] == "18.00"

    assert payments_report_response.status_code == 200
    assert payments_report_response.json()[0]["payment_method"] == "CASH"
    assert payments_report_response.json()[0]["revenue"] == "28.00"

    assert cash_register_report_response.status_code == 200
    assert cash_register_report_response.json(
    )[0]["totals"]["sales_amount"] == "28.00"

    assert expenses_report_response.status_code == 200
    assert expenses_report_response.json()[0]["category"] == "INGREDIENTS"
    assert expenses_report_response.json()[0]["amount"] == "10.00"
