from .consensus.checks import MAX_VALUE
from pydantic import BaseModel, Field
from pydantic import ValidationError
from . import constants
import msgpack

class CategoryValidation(BaseModel):
    category: int = Field(ge=1, le=5)

class CreateValidation(CategoryValidation):
    ticker: str = Field(min_length=3, max_length=8)
    value: int = Field(ge=1, le=MAX_VALUE)
    decimals: int = Field(ge=1, le=8)
    reissuable: bool

class IssueValidation(CategoryValidation):
    ticker: str = Field(min_length=3, max_length=8)
    value: int = Field(ge=1, le=MAX_VALUE)

class TransferValidation(CategoryValidation):
    ticker: str = Field(min_length=3, max_length=8)
    value: int = Field(ge=1, le=MAX_VALUE)

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
                    "a": data.value,
                    "t": data.ticker
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

                TransferValidation(**payload)

        except ValidationError as e:
            print("Failed to decode payload:", e)
            return None

        return payload
