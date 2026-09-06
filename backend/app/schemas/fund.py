from datetime import date as Date, datetime
from pydantic import BaseModel, ConfigDict, Field


class FundCreate(BaseModel):
    date: Date
    amount: int = Field(gt=0)
    source_type: str = Field(default="other", max_length=30)
    note: str = Field(default="")


class FundUpdate(BaseModel):
    date: Date | None = None
    amount: int | None = Field(default=None, gt=0)
    source_type: str | None = Field(default=None, max_length=30,)
    note: str | None = None


class FundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date: Date
    amount: int
    source_type: str
    note: str
    created_at: datetime
    updated_at: datetime