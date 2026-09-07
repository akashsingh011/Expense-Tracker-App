from sqlalchemy import select, extract, func
from sqlalchemy.orm import Session

from app.models.expense import Expense


def get_monthly_summary(
    db: Session,
    user_id: int,
    year: int,
) -> list[dict]:

    statement = (
        select(
            extract("month", Expense.date).label("month"),
            func.sum(Expense.amount).label("total_expenses"),
            func.count(Expense.id).label("total_transactions"),
        )
        .where(
            Expense.user_id == user_id,
            extract("year", Expense.date) == year,
        )
        .group_by(extract("month", Expense.date))
        .order_by(extract("month", Expense.date).asc())
    )

    rows = db.execute(statement).all()

    return [
        {
            "year": year,
            "month": int(row.month),
            "total_expenses": int(row.total_expenses),
            "total_transactions": int(row.total_transactions),
        }
        for row in rows
    ]