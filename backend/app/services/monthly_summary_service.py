from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.expense import Expense


def get_monthly_summary(
    db: Session,
    user_id: int,
    year: int,
    month: int,
) -> dict:

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    statement = select(
        func.sum(Expense.amount).label("total_expenses"),
        func.count(Expense.id).label("total_transactions"),
    ).where(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date < end_date,
    )

    row = db.execute(statement).one()

    return {
        "year": year,
        "month": month,
        "total_expenses": int(row.total_expenses or 0),
        "total_transactions": int(row.total_transactions or 0),
    }