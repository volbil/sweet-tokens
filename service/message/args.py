from pydantic import BaseModel, Field
from ..consensus import MAX_VALUE

class CreateArgs(BaseModel):
    ticker: str = Field(min_length=3, max_length=8)
    value: int = Field(ge=1, le=MAX_VALUE)
    decimals: int = Field(ge=1, le=8)
    reissuable: bool

class TransferArgs(BaseModel):
    ticker: str = Field(min_length=3, max_length=8)
    value: int = Field(ge=1, le=MAX_VALUE)

class IssueArgs(BaseModel):
    ticker: str = Field(min_length=3, max_length=8)
    value: int = Field(ge=1, le=MAX_VALUE)
