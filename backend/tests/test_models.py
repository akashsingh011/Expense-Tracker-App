from app.models import Expense, Fund, User


def test_user_relationships():
    assert hasattr(User, "expenses")
    assert hasattr(User, "funds")


def test_expense_user_relationship():
    assert hasattr(Expense, "user")


def test_fund_user_relationship():
    assert hasattr(Fund, "user")