import httpx
from datetime import date as dt

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def register(self, username: str, email: str, password: str) -> dict:
        response = httpx.post(
            self._url("/api/v1/auth/register"),
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

        response.raise_for_status()
        return response.json()

    def login(self, email: str, password: str) -> dict:
        response = httpx.post(
            self._url("/api/v1/auth/login"),
            json={
                "email": email,
                "password": password,
            },
        )

        response.raise_for_status()
        return response.json()

    def get_me(self, token: str) -> dict:
        response = httpx.get(
            self._url("/api/v1/auth/me"),
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        response.raise_for_status()
        return response.json()

    def get_expenses(
        self,
        token: str,
        start_date: str | None = None,
        end_date: str | None = None,
        category: str | None = None,
    ) -> list:
        params = {}

        if start_date:
            params["start_date"] = start_date

        if end_date:
            params["end_date"] = end_date

        if category:
            params["category"] = category

        response = httpx.get(
            self._url("/api/v1/expenses"),
            headers={
                "Authorization": f"Bearer {token}",
            },
            params=params,
        )

        response.raise_for_status()
        return response.json()


    def create_expense(
        self,
        token: str,
        date: str,
        amount: int,
        category: str,
        subcategory: str = "",
        note: str = "",
    ) -> dict:
        response = httpx.post(
            self._url("/api/v1/expenses"),
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "date": date,
                "amount": amount,
                "category": category,
                "subcategory": subcategory,
                "note": note,
            },
        )
        response.raise_for_status()
        return response.json()

    def update_expense(
        self,
        token: str,
        expense_id: int,
        date: str | None = None,
        amount: int | None = None,
        category: str | None = None,
        subcategory: str | None = None,
        note: str | None = None,
    ) -> dict:
        data = {}

        if date is not None:
            data["date"] = date

        if amount is not None:
            data["amount"] = amount

        if category is not None:
            data["category"] = category

        if subcategory is not None:
            data["subcategory"] = subcategory

        if note is not None:
            data["note"] = note

        response = httpx.patch(
            self._url(f"/api/v1/expenses/{expense_id}"),
            headers={
                "Authorization": f"Bearer {token}",
            },
            json=data,
        )
        response.raise_for_status()
        return response.json()

    def delete_expense(
        self,
        token: str,
        expense_id: int,
    ) -> None:
        response = httpx.delete(
            self._url(f"/api/v1/expenses/{expense_id}"),
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        response.raise_for_status()

    # Funds
    def get_funds(
        self,
        token: str,
        start_date: str | None = None,
        end_date: str | None = None,
        source_type: str | None = None,
    ) -> list:
        params = {}

        if start_date:
            params["start_date"] = start_date

        if end_date:
            params["end_date"] = end_date

        if source_type:
            params["source_type"] = source_type

        response = httpx.get(
            self._url("/api/v1/funds"),
            headers={
                "Authorization": f"Bearer {token}",
            },
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def create_fund(
        self,
        token: str,
        date: str,
        amount: int,
        source_type: str = "other",
        note: str = "",
    ) -> dict:
        response = httpx.post(
            self._url("/api/v1/funds"),
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "date": date,
                "amount": amount,
                "source_type": source_type,
                "note": note,
            },
        )
        response.raise_for_status()
        return response.json()

    def update_fund(
        self,
        token: str,
        fund_id: int,
        date: str | None = None,
        amount: int | None = None,
        source_type: str | None = None,
        note: str | None = None,
    ) -> dict:
        data = {}

        if date is not None:
            data["date"] = date

        if amount is not None:
            data["amount"] = amount

        if source_type is not None:
            data["source_type"] = source_type

        if note is not None:
            data["note"] = note

        response = httpx.patch(
            self._url(f"/api/v1/funds/{fund_id}"),
            headers={
                "Authorization": f"Bearer {token}",
            },
            json=data,
        )
        response.raise_for_status()
        return response.json()

    def delete_fund(
        self,
        token: str,
        fund_id: int,
    ) -> None:
        response = httpx.delete(
            self._url(f"/api/v1/funds/{fund_id}"),
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        response.raise_for_status()

    def get_wallet_balance(self, token: str) -> dict:
        response = httpx.get(
            self._url("/api/v1/wallet/balance"),
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    def get_expense_summary(
        self,
        token: str,
        start_date: str | None = None,
        end_date: str | None = None,
        # category: str | None = None,
    ) -> dict:
        params = {}

        if start_date:
            params["start_date"] = start_date

        if end_date:
            params["end_date"] = end_date

        # if category:
        #     params["category"] = category

        response = httpx.get(
            self._url("/api/v1/expenses/summary"),
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )

        response.raise_for_status()
        return response.json()

    def get_expense_years(
        self,
        token: str,
    ) -> list[int]:
        response = httpx.get(
            self._url("/api/v1/expenses"),
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        expenses = response.json()

        if not expenses:
            return []

        import pandas as pd
        df = pd.DataFrame(expenses)
        df["date"] = pd.to_datetime(df["date"])
        years = sorted(df["date"].dt.year.unique().tolist(), reverse=True)
        return [int(y) for y in years]


    def get_monthly_expense_summary(
        self,
        token: str,
        year: int,
        month: int,
    ) -> dict:
        response = httpx.get(
            self._url("/api/v1/expenses/monthly-summary"),
            headers={"Authorization": f"Bearer {token}"},
            params={
                "year": year,
                "month": month,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_all_funds(self, token: str) -> list:
        response = httpx.get(
            self._url("/api/v1/funds"),
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()