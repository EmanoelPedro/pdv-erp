from datetime import UTC, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.cash_register import CashRegisterSession
from app.domain.catalog import Category, Product
from app.domain.expense import Expense, ExpenseCategory
from app.domain.sale import PaymentBreakdown, PaymentMethod, Sale, SaleItem
from app.domain.shared import utc_now
from app.domain.user import User, UserRole
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.catalog_repository import CategoryRepository, ProductRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.report_repository import ReportFilters, ReportRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.user_repository import UserRepository
from app.services.cash_register_service import CashRegisterService
from app.services.dashboard_service import DashboardService
from app.services.report_service import ReportService
from app.services.security import hash_pin


def _at(day_offset: int, hour: int, minute: int = 0) -> datetime:
    base_day = utc_now().date() + timedelta(days=day_offset)
    return datetime.combine(base_day, time(hour=hour, minute=minute), tzinfo=UTC)


def _create_user(db_session: Session, username: str, role: UserRole) -> User:
    user = User.create(
        full_name=username.title(),
        username=username,
        role=role,
        pin_hash=hash_pin("1234"),
    )
    return UserRepository(db_session).create(user)


def _create_product(
    db_session: Session,
    *,
    category_name: str,
    product_name: str,
    price: str,
) -> Product:
    category = CategoryRepository(db_session).create(
        Category.create(name=category_name, created_at=_at(-1, 7))
    )
    return ProductRepository(db_session).create(
        Product.create(
            category_id=category.id,
            name=product_name,
            price=Decimal(price),
            created_at=_at(-1, 7),
        ),
    )


def _create_session(
    db_session: Session,
    *,
    opening_amount: str,
    opened_at: datetime,
    closing_amount: str | None = None,
    closed_at: datetime | None = None,
) -> CashRegisterSession:
    repository = CashRegisterSessionRepository(db_session)
    session = repository.create(
        CashRegisterSession.open(Decimal(opening_amount), opened_at=opened_at)
    )
    if closing_amount is None:
        return session
    return repository.update(session.close(Decimal(closing_amount), closed_at=closed_at))


def _create_sale(
    db_session: Session,
    *,
    session_id,
    seller_id,
    product: Product,
    quantity: int,
    payment_method: PaymentMethod,
    created_at: datetime,
) -> None:
    item = SaleItem.from_product(product, quantity=quantity, created_at=created_at)
    payment = PaymentBreakdown.create(payment_method, item.total_price)
    sale = Sale.create(
        cash_register_session_id=session_id,
        seller_user_id=seller_id,
        items=(item,),
        payment=payment,
        created_at=created_at,
    )
    SaleRepository(db_session).create(sale)


def _create_expense(
    db_session: Session,
    *,
    description: str,
    amount: str,
    category: ExpenseCategory,
    payment_method: PaymentMethod,
    created_by_id,
    session_id,
    expense_date: datetime,
) -> None:
    expense = Expense.create(
        description=description,
        amount=Decimal(amount),
        category=category,
        payment_method=payment_method,
        created_by_user_id=created_by_id,
        cash_register_session_id=session_id,
        expense_date=expense_date,
        created_at=expense_date,
    )
    ExpenseRepository(db_session).create(expense)


def test_dashboard_summary_calculates_today_metrics(db_session: Session) -> None:
    owner = _create_user(db_session, "owner-dashboard", UserRole.OWNER)
    pastel = _create_product(
        db_session,
        category_name="Salgados",
        product_name="Pastel",
        price="12.00",
    )
    caldo = _create_product(
        db_session,
        category_name="Bebidas",
        product_name="Caldo de Cana",
        price="8.00",
    )

    today_session = _create_session(
        db_session,
        opening_amount="150.00",
        opened_at=_at(0, 8),
    )
    _create_session(
        db_session,
        opening_amount="100.00",
        opened_at=_at(-1, 8),
        closing_amount="110.00",
        closed_at=_at(0, 21),
    )

    _create_sale(
        db_session,
        session_id=today_session.id,
        seller_id=owner.id,
        product=pastel,
        quantity=3,
        payment_method=PaymentMethod.CASH,
        created_at=_at(0, 9, 15),
    )
    _create_sale(
        db_session,
        session_id=today_session.id,
        seller_id=owner.id,
        product=caldo,
        quantity=1,
        payment_method=PaymentMethod.PIX,
        created_at=_at(0, 10, 30),
    )
    _create_sale(
        db_session,
        session_id=today_session.id,
        seller_id=owner.id,
        product=caldo,
        quantity=2,
        payment_method=PaymentMethod.CASH,
        created_at=_at(-1, 15, 0),
    )
    _create_expense(
        db_session,
        description="Compra de queijo",
        amount="15.00",
        category=ExpenseCategory.INGREDIENTS,
        payment_method=PaymentMethod.CASH,
        created_by_id=owner.id,
        session_id=today_session.id,
        expense_date=_at(0, 11, 0),
    )
    db_session.commit()

    summary = DashboardService(ReportRepository(db_session)).get_today_summary()

    assert summary.revenue_today == Decimal("44.00")
    assert summary.expenses_today == Decimal("15.00")
    assert summary.profit_estimate_today == Decimal("29.00")
    assert summary.average_ticket_today == Decimal("22.00")
    assert summary.sales_count_today == 2
    assert summary.latest_cash_difference == Decimal("10.00")
    assert summary.best_selling_product_today is not None
    assert summary.best_selling_product_today.product_name == "Pastel"
    assert summary.best_selling_product_today.quantity_sold == 3
    assert summary.best_category_today is not None
    assert summary.best_category_today.category_name == "Salgados"
    assert len(summary.sales_by_hour_today) == 24
    assert next(
        point for point in summary.sales_by_hour_today if point.hour == "09:00"
    ).revenue == Decimal("36.00")
    assert next(
        point for point in summary.sales_by_hour_today if point.hour == "10:00"
    ).revenue == Decimal("8.00")
    assert len(summary.revenue_last_7_days) == 7
    assert summary.revenue_last_7_days[-1].revenue == Decimal("44.00")
    assert summary.revenue_last_7_days[-2].revenue == Decimal("16.00")


def test_report_service_applies_filters_and_percentages(db_session: Session) -> None:
    owner = _create_user(db_session, "owner-reports", UserRole.OWNER)
    employee = _create_user(db_session, "employee-reports", UserRole.EMPLOYEE)
    pastel = _create_product(
        db_session,
        category_name="Salgados",
        product_name="Pastel",
        price="10.00",
    )
    refrigerante = _create_product(
        db_session,
        category_name="Bebidas",
        product_name="Refrigerante",
        price="6.00",
    )

    owner_session = _create_session(
        db_session,
        opening_amount="120.00",
        opened_at=_at(0, 8),
    )
    employee_session = _create_session(
        db_session,
        opening_amount="120.00",
        opened_at=_at(0, 12),
    )

    _create_sale(
        db_session,
        session_id=owner_session.id,
        seller_id=owner.id,
        product=pastel,
        quantity=2,
        payment_method=PaymentMethod.CASH,
        created_at=_at(0, 9, 0),
    )
    _create_sale(
        db_session,
        session_id=owner_session.id,
        seller_id=owner.id,
        product=pastel,
        quantity=1,
        payment_method=PaymentMethod.PIX,
        created_at=_at(0, 10, 0),
    )
    _create_sale(
        db_session,
        session_id=employee_session.id,
        seller_id=employee.id,
        product=refrigerante,
        quantity=5,
        payment_method=PaymentMethod.CASH,
        created_at=_at(0, 13, 0),
    )
    _create_expense(
        db_session,
        description="Retirada do caixa",
        amount="10.00",
        category=ExpenseCategory.WITHDRAWAL,
        payment_method=PaymentMethod.CASH,
        created_by_id=owner.id,
        session_id=owner_session.id,
        expense_date=_at(0, 14, 0),
    )
    _create_expense(
        db_session,
        description="Consumo interno",
        amount="30.00",
        category=ExpenseCategory.PERSONAL_USE,
        payment_method=PaymentMethod.PIX,
        created_by_id=employee.id,
        session_id=employee_session.id,
        expense_date=_at(0, 15, 0),
    )
    db_session.commit()

    cash_register_service = CashRegisterService(
        repository=CashRegisterSessionRepository(db_session),
        sale_repository=SaleRepository(db_session),
        expense_repository=ExpenseRepository(db_session),
    )
    service = ReportService(ReportRepository(db_session), cash_register_service)

    category_filter = ReportFilters(
        start_date=utc_now().date(),
        end_date=utc_now().date(),
        category_id=pastel.category_id,
        user_id=owner.id,
    )
    product_rows = service.list_product_performance(category_filter)
    sales_rows = service.list_sales_summary(
        ReportFilters(
            start_date=utc_now().date(),
            end_date=utc_now().date(),
            user_id=owner.id,
        )
    )
    payment_rows = service.list_payment_methods(
        ReportFilters(
            start_date=utc_now().date(),
            end_date=utc_now().date(),
            user_id=owner.id,
        )
    )
    expense_rows = service.list_expense_analysis(
        ReportFilters(
            start_date=utc_now().date(),
            end_date=utc_now().date(),
            user_id=employee.id,
        )
    )

    assert len(product_rows) == 1
    assert product_rows[0].product_name == "Pastel"
    assert product_rows[0].quantity_sold == 3
    assert product_rows[0].revenue == Decimal("30.00")
    assert product_rows[0].average_sale_participation == Decimal("100.00")

    assert len(sales_rows) == 1
    assert sales_rows[0].gross_sales == Decimal("30.00")
    assert sales_rows[0].discounts == Decimal("0.00")
    assert sales_rows[0].expenses == Decimal("10.00")
    assert sales_rows[0].estimated_result == Decimal("20.00")

    assert len(payment_rows) == 2
    assert payment_rows[0].payment_method == PaymentMethod.CASH
    assert payment_rows[0].percentage_of_total == Decimal("66.67")
    assert payment_rows[1].payment_method == PaymentMethod.PIX
    assert payment_rows[1].percentage_of_total == Decimal("33.33")

    assert len(expense_rows) == 1
    assert expense_rows[0].category == ExpenseCategory.PERSONAL_USE
    assert expense_rows[0].amount == Decimal("30.00")
    assert expense_rows[0].percentage_of_total == Decimal("100.00")
