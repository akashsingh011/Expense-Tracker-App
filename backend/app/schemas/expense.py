from datetime import date as Date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    date: Date
    amount: int = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    subcategory: str = Field(default="", max_length=100)
    note: str = Field(default="")


class ExpenseUpdate(BaseModel):
    date: Date | None = None
    amount: int | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    subcategory: str | None = Field(default=None, max_length=100)
    note: str | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date: Date
    amount: int
    category: str
    subcategory: str
    note: str
    created_at: datetime
    updated_at: datetime