from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense


def get_monthly_summary(db: Session, user_id: int, year: int, month: int,) -> dict:
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    statement = select(
        func.coalesce(func.sum(Expense.amount), 0),
        func.count(Expense.id),
    ).where(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date < end_date,
    )

    total_expenses, total_transactions = db.execute(
        statement
    ).one()

    return {
        "year": year,
        "month": month,
        "total_expenses": total_expenses,
        "total_transactions": total_transactions,
    }