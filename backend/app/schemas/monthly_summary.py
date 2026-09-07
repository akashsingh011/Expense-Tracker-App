from pydantic import BaseModel
from typing import List


class MonthlyEntry(BaseModel):
    year: int
    month: int
    total_expenses: int
    total_transactions: int


class MonthlySummaryResponse(BaseModel):
    year: int
    entries: List[MonthlyEntry]