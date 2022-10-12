from pydantic import ValidationError
from pydantic import conint, constr
from pydantic import BaseModel
import constants
import msgpack

class CategoryValidation(BaseModel):
    category: conint(ge=1, le=5)

class CreateValidation(CategoryValidation):
    amount: float
    name: constr(strip_whitespace=True, min_length=1, max_length=24)
    ticker: constr(strip_whitespace=True, min_length=1, max_length=8)
    reissuable: bool

class IssueValidation(CategoryValidation):
    amount: float
    ticker: constr(strip_whitespace=True, min_length=1, max_length=8)

class TransferValidation(CategoryValidation):
    amount: float
    ticker: constr(strip_whitespace=True, min_length=1, max_length=8)

class BanValidation(CategoryValidation):
    address: constr(strip_whitespace=True, min_length=40, max_length=40)

class UnbanValidation(CategoryValidation):
    address: constr(strip_whitespace=True, min_length=40, max_length=40)

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
                # Do this to remove additional fields that are not part of the payload
                payload = {
                    "c": data.category,
                    "a": data.amount,
                    "n": data.name,
                    "t": data.ticker,
                    "r": data.reissuable
                }

            elif category == constants.ISSUE:
                data = IssueValidation(**payload)
                payload = {
                    "c": data.category,
                    "a": data.amount,
                    "t": data.ticker
                }

            elif category == constants.TRANSFER:
                data = TransferValidation(**payload)
                payload = {
                    "c": data.category,
                    "a": data.amount,
                    "t": data.ticker
                }

            elif category == constants.BAN:
                data = BanValidation(**payload)
                payload = {
                    "c": data.category,
                    "a": data.address
                }

            elif category == constants.UNBAN:
                data = UnbanValidation(**payload)
                payload = {
                    "c": data.category,
                    "a": data.address
                }

        except ValidationError:
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
                payload["amount"] = payload.pop("a")
                payload["name"] = payload.pop("n")
                payload["ticker"] = payload.pop("t")
                payload["reissuable"] = payload.pop("r")

                CreateValidation(**payload)

            elif category == constants.ISSUE:
                payload["amount"] = payload.pop("a")
                payload["ticker"] = payload.pop("t")

                IssueValidation(**payload)

            elif category == constants.TRANSFER:
                payload["amount"] = payload.pop("a")
                payload["ticker"] = payload.pop("t")

                TransferValidation(**payload)

            elif category == constants.BAN:
                payload["address"] = payload.pop("a")

                BanValidation(**payload)

            elif category == constants.UNBAN:
                payload["address"] = payload.pop("a")

                UnbanValidation(**payload)

        except ValidationError:
            return None

        return payload
