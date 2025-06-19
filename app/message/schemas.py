from app.schemas import CustomModel
from pydantic import Field
from app import constants


class CreateArgs(CustomModel):
    decimals: int = Field(ge=constants.MIN_DECIMALS, le=constants.MAX_DECIMALS)
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    reissuable: bool

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
    )


class TransferArgs(CustomModel):
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    lock: int | None = Field(default=None, ge=1)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
    )


class BurnArgs(CustomModel):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
    )


class IssueArgs(CustomModel):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
    )


class CostArgs(CustomModel):
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    type: str = Field(pattern=constants.TOKEN_TYPE_RE)
    action: str = Field(pattern=constants.ACTIONS_RE)
