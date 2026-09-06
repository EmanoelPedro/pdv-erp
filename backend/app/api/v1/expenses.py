from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_current_user, get_expense_service
from app.domain.expense import ExpenseCategory
from app.domain.user import User
from app.schemas.expense import CreateExpenseRequest, ExpenseResponse, UpdateExpenseRequest
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: CreateExpenseRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
) -> ExpenseResponse:
    expense = service.create_expense(
        description=payload.description,
        amount=payload.amount,
        category=payload.category,
        payment_method=payload.payment_method,
        created_by=current_user,
        cash_register_session_id=payload.cash_register_session_id,
        notes=payload.notes,
        expense_date=payload.expense_date,
    )
    return ExpenseResponse.from_domain(expense)


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    category: Annotated[ExpenseCategory | None, Query()] = None,
    cash_register_session_id: Annotated[UUID | None, Query()] = None,
) -> list[ExpenseResponse]:
    expenses = service.list_expenses(
        actor=current_user,
        start_date=start_date,
        end_date=end_date,
        category=category,
        cash_register_session_id=cash_register_session_id,
    )
    return [ExpenseResponse.from_domain(expense) for expense in expenses]


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
) -> ExpenseResponse:
    expense = service.get_expense(expense_id, current_user)
    return ExpenseResponse.from_domain(expense)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: UUID,
    payload: UpdateExpenseRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
) -> ExpenseResponse:
    expense = service.update_expense(
        expense_id,
        description=payload.description,
        amount=payload.amount,
        category=payload.category,
        payment_method=payload.payment_method,
        actor=current_user,
        cash_register_session_id=payload.cash_register_session_id,
        notes=payload.notes,
        expense_date=payload.expense_date,
    )
    return ExpenseResponse.from_domain(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
) -> Response:
    service.delete_expense(expense_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
