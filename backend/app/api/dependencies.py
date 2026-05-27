from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_db
from app.domain.exceptions import AuthenticationRequiredError, OwnerPermissionRequiredError
from app.domain.user import User
from app.repositories.auth_session_repository import AuthSessionRepository
from app.repositories.cash_register_repository import CashRegisterSessionRepository
from app.repositories.catalog_repository import CategoryRepository, ProductRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.cash_register_service import CashRegisterService
from app.services.catalog_service import CatalogService
from app.services.expense_service import ExpenseService
from app.services.report_service import ReportService
from app.services.sale_service import SaleService

AuthorizationHeader = Annotated[str | None, Header(alias="Authorization")]


def get_auth_service(
    db: Annotated[Session, Depends(get_db)],
) -> AuthService:
    settings = get_settings()
    return AuthService(
        user_repository=UserRepository(db),
        auth_session_repository=AuthSessionRepository(db),
        session_days=settings.auth_session_days,
    )


def get_current_user(
    authorization: AuthorizationHeader = None,
    auth_service: Annotated[AuthService, Depends(get_auth_service)] = None,
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise AuthenticationRequiredError("Authentication is required.")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise AuthenticationRequiredError("Authentication is required.")

    return auth_service.authenticate(token)


def get_optional_current_user(
    authorization: AuthorizationHeader = None,
    auth_service: Annotated[AuthService, Depends(get_auth_service)] = None,
) -> User | None:
    if authorization is None:
        return None
    if not authorization.startswith("Bearer "):
        return None

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        return None

    return auth_service.authenticate(token)


def get_current_owner_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role.value != "OWNER":
        raise OwnerPermissionRequiredError(
            "Owner approval is required for this action.")
    return current_user


def get_cash_register_service(
    db: Annotated[Session, Depends(get_db)],
) -> CashRegisterService:
    repository = CashRegisterSessionRepository(db)
    return CashRegisterService(
        repository=repository,
        sale_repository=SaleRepository(db),
        expense_repository=ExpenseRepository(db),
    )


def get_expense_service(
    db: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> ExpenseService:
    return ExpenseService(
        expense_repository=ExpenseRepository(db),
        cash_register_repository=CashRegisterSessionRepository(db),
        auth_service=auth_service,
    )


def get_dashboard_service(
    db: Annotated[Session, Depends(get_db)],
) -> DashboardService:
    return DashboardService(report_repository=ReportRepository(db))


def get_catalog_service(
    db: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> CatalogService:
    return CatalogService(
        category_repository=CategoryRepository(db),
        product_repository=ProductRepository(db),
        auth_service=auth_service,
    )


def get_sale_service(
    db: Annotated[Session, Depends(get_db)],
) -> SaleService:
    return SaleService(
        sale_repository=SaleRepository(db),
        product_repository=ProductRepository(db),
        cash_register_repository=CashRegisterSessionRepository(db),
    )


def get_report_service(
    db: Annotated[Session, Depends(get_db)],
) -> ReportService:
    return ReportService(
        report_repository=ReportRepository(db),
        cash_register_service=CashRegisterService(
            repository=CashRegisterSessionRepository(db),
            sale_repository=SaleRepository(db),
            expense_repository=ExpenseRepository(db),
        ),
    )
