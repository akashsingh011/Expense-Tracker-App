from pydantic import BaseModel

class CategorySummary(BaseModel):
    total: int
    transactions: int


class ExpenseSummaryResponse(BaseModel):
    total_expenses: int
    total_transactions: int
    by_category: dict[str, CategorySummary]
    by_subcategory: dict[str, CategorySummary]