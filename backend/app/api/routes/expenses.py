from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
)
from app.schemas.monthly_summary import MonthlySummaryResponse
from app.schemas.summary import ExpenseSummaryResponse
from app.services.expense_service import (
    create_expense,
    delete_expense,
    get_expense,
    list_expenses,
    update_expense,
)
from app.services.monthly_summary_service import get_monthly_summary
from app.services.summary_service import get_expense_summary


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_endpoint(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_expense(
        db=db,
        user_id=current_user.id,
        expense_data=expense_data,
    )


@router.get(
    "",
    response_model=list[ExpenseResponse],
)
def list_expenses_endpoint(
    start_date: Date | None = None,
    end_date: Date | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_expenses(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        category=category,
    )


@router.get(
    "/summary",
    response_model=ExpenseSummaryResponse,
)
def expense_summary_endpoint(
    start_date: Date | None = None,
    end_date: Date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_expense_summary(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/monthly-summary",
    response_model=MonthlySummaryResponse,
)
def monthly_summary_endpoint(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12",
        )

    return get_monthly_summary(
        db=db,
        user_id=current_user.id,
        year=year,
        month=month,
    )


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def get_expense_endpoint(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = get_expense(
        db=db,
        user_id=current_user.id,
        expense_id=expense_id,
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return expense


@router.patch(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def update_expense_endpoint(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = update_expense(
        db=db,
        user_id=current_user.id,
        expense_id=expense_id,
        expense_data=expense_data,
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return expense


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense_endpoint(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_expense(
        db=db,
        user_id=current_user.id,
        expense_id=expense_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return None