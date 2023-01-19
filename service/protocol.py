from pydantic import BaseModel, Field
from pydantic import ValidationError
from typing import Union
from . import constants
import msgpack

class CategoryValidation(BaseModel):
    category: int = Field(ge=constants.CREATE, le=constants.BURN)

class CreateValidation(CategoryValidation):
    decimals: int = Field(ge=constants.MIN_DECIMALS, le=constants.MAX_DECIMALS)
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    reissuable: bool

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
        regex=constants.TICKER_RE
    )

class IssueValidation(CategoryValidation):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
        regex=constants.TICKER_RE
    )

class TransferValidation(CategoryValidation):
    lock: Union[int, None] = Field(default=None, ge=1)
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
        regex=constants.TICKER_RE
    )

class BurnValidation(CategoryValidation):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH,
        regex=constants.TICKER_RE
    )

class Protocol(object):
    @classmethod
    def encode(cls, payload):
        # Validate category
        try:
            CategoryValidation(**payload)
        except ValidationError:
            return None

        category = payload["category"]

        # Validate the rest of the payload
        try:
            if category == constants.CREATE:
                data = CreateValidation(**payload)
                payload = {
                    "r": data.reissuable,
                    "d": data.decimals,
                    "c": data.category,
                    "a": data.value,
                    "t": data.ticker
                }

            elif category == constants.ISSUE:
                data = IssueValidation(**payload)
                payload = {
                    "c": data.category,
                    "a": data.value,
                    "t": data.ticker
                }

            elif category == constants.TRANSFER:
                data = TransferValidation(**payload)
                payload = {
                    "c": data.category,
                    "t": data.ticker,
                    "a": data.value,
                    "l": data.lock
                }

            elif category == constants.BURN:
                data = BurnValidation(**payload)
                payload = {
                    "c": data.category,
                    "t": data.ticker,
                    "a": data.value
                }

            elif category == constants.BAN:
                data = CategoryValidation(**payload)
                payload = {
                    "c": data.category
                }

            elif category == constants.UNBAN:
                data = CategoryValidation(**payload)
                payload = {
                    "c": data.category
                }

        except ValidationError as e:
            print("Failed to encode payload:", e)
            return None

        return msgpack.packb(payload).hex()

    @classmethod
    def decode(cls, data):
        # Validate bytes
        try:
            data = bytes.fromhex(data)
            payload = msgpack.unpackb(data)
        except ValueError:
            return None

        if "c" not in payload:
            return None

        payload["category"] = payload.pop("c")

        # Validate category
        try:
            CategoryValidation(**payload)
        except ValidationError:
            return None

        category = payload["category"]

        # Validate the rest of the payload
        try:
            if category == constants.CREATE:
                payload["value"] = payload.pop("a")
                payload["ticker"] = payload.pop("t")
                payload["decimals"] = payload.pop("d")
                payload["reissuable"] = payload.pop("r")

                CreateValidation(**payload)

            elif category == constants.ISSUE:
                payload["value"] = payload.pop("a")
                payload["ticker"] = payload.pop("t")

                IssueValidation(**payload)

            elif category == constants.TRANSFER:
                payload["value"] = payload.pop("a")
                payload["ticker"] = payload.pop("t")
                payload["lock"] = payload.pop("l")

                TransferValidation(**payload)

            elif category == constants.BURN:
                payload["value"] = payload.pop("a")
                payload["ticker"] = payload.pop("t")

                BurnValidation(**payload)

        except ValidationError as e:
            print("Failed to decode payload:", e)
            return None

        return payload
