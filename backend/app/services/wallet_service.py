from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.fund import Fund


def get_wallet_balance(db: Session, user_id: int,) -> dict:
    total_funds = db.scalar(
        select(func.coalesce(func.sum(Fund.amount), 0))
        .where(Fund.user_id == user_id)
    )

    total_expenses = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(Expense.user_id == user_id)
    )

    wallet_balance = total_funds - total_expenses

    if wallet_balance < 0:
        status = "overdrawn"
        warning = "Your wallet balance is negative."
    elif total_funds > 0 and wallet_balance < (total_funds * 0.10):
        status = "low_balance"
        warning = "Your wallet balance is below 10% of total funds."
    else:
        status = "healthy"
        warning = None

    return {
        "total_funds": total_funds,
        "total_expenses": total_expenses,
        "wallet_balance": wallet_balance,
        "status": status,
        "warning": warning,
    }