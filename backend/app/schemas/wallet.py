from pydantic import BaseModel

class WalletResponse(BaseModel):
    total_funds: int
    total_expenses: int
    wallet_balance: int
    status: str
    warning: str | None = None