from datetime import date as Date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(
    db: Session,
    user_id: int,
    expense_data: ExpenseCreate,
) -> Expense:
    expense = Expense(
        user_id=user_id,
        date=expense_data.date,
        amount=expense_data.amount,
        category=expense_data.category,
        subcategory=expense_data.subcategory,
        note=expense_data.note,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


def get_expense(
    db: Session,
    user_id: int,
    expense_id: int,
) -> Expense | None:
    statement = select(Expense).where(
        Expense.id == expense_id,
        Expense.user_id == user_id,
    )

    return db.scalar(statement)


def list_expenses(
    db: Session,
    user_id: int,
    start_date: Date | None = None,
    end_date: Date | None = None,
    category: str | None = None,
) -> list[Expense]:
    statement = select(Expense).where(
        Expense.user_id == user_id
    )

    if start_date is not None:
        statement = statement.where(
            Expense.date >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            Expense.date <= end_date
        )

    if category is not None:
        statement = statement.where(
            func.lower(Expense.category) == category.strip().lower()
        )

    statement = statement.order_by(
        Expense.date.asc(),
        Expense.id.asc(),
    )

    return list(db.scalars(statement).all())


def update_expense(
    db: Session,
    user_id: int,
    expense_id: int,
    expense_data: ExpenseUpdate,
) -> Expense | None:
    expense = get_expense(
        db=db,
        user_id=user_id,
        expense_id=expense_id,
    )

    if expense is None:
        return None

    update_data = expense_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return expense


def delete_expense(
    db: Session,
    user_id: int,
    expense_id: int,
) -> bool:
    expense = get_expense(
        db=db,
        user_id=user_id,
        expense_id=expense_id,
    )

    if expense is None:
        return False

    db.delete(expense)
    db.commit()

    return True