from pydantic import BaseModel, Field
from typing import Union
from .. import constants

class CreateArgs(BaseModel):
    decimals: int = Field(ge=constants.MIN_DECIMALS, le=constants.MAX_DECIMALS)
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    reissuable: bool

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class TransferArgs(BaseModel):
    lock: Union[int, None] = Field(default=None, ge=1)
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class BurnArgs(BaseModel):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class IssueArgs(BaseModel):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class CostArgs(BaseModel):
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    type: str = Field(regex=constants.TOKEN_TYPE_RE)
    action: str = Field(regex=constants.ACTIONS_RE)
