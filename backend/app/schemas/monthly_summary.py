from pydantic import BaseModel


class MonthlySummaryResponse(BaseModel):
    year: int
    month: int
    total_expenses: int
    total_transactions: int