from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.expense import Expense


def get_expense_summary(
        db: Session, 
        user_id: int, 
        start_date: date | None = None, 
        end_date: date | None = None,
    ) -> dict:
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

    statement = statement.order_by(
        Expense.date.asc(),
        Expense.id.asc(),
    )

    expenses = list(db.scalars(statement).all())

    total_expenses = sum(
        expense.amount
        for expense in expenses
    )

    by_category: dict[str, dict[str, int]] = {}
    by_subcategory: dict[str, dict[str, int]] = {}

    for expense in expenses:
        category = expense.category
        subcategory = expense.subcategory

        if category not in by_category:
            by_category[category] = {
                "total": 0,
                "transactions": 0,
            }

        by_category[category]["total"] += expense.amount
        by_category[category]["transactions"] += 1

        if subcategory not in by_subcategory:
            by_subcategory[subcategory] = {
                "total": 0,
                "transactions": 0,
            }

        by_subcategory[subcategory]["total"] += expense.amount
        by_subcategory[subcategory]["transactions"] += 1

    return {
        "total_expenses": total_expenses,
        "total_transactions": len(expenses),
        "by_category": by_category,
        "by_subcategory": by_subcategory,
    }