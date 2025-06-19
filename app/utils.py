from functools import lru_cache
from dynaconf import Dynaconf
from datetime import datetime
from decimal import Decimal
import aiohttp
import json
import math


@lru_cache()
def get_settings():
    """Returns lru cached system settings"""

    return Dynaconf(
        settings_files=["settings.toml"],
        default_env="default",
        environments=True,
    )


# Hack for converting flot to decimal
def float_to_decimal(value: float) -> Decimal:
    return Decimal(str(value))


# Convest timestamp to UTC datetime
def from_timestamp(timestamp: int):
    return utcfromtimestamp(timestamp) if timestamp else None


# Convert datetime to timestamp
def to_timestamp(date: datetime | None) -> int | None:
    date = date.replace(tzinfo=timezone.utc) if date else date
    return int(date.timestamp()) if date else None


# Helper function for toroise pagination
def pagination(page, size=20):
    limit = size
    offset = (limit * (page)) - limit

    return limit, offset, size


# Helper function to make pagication dict for api
def pagination_dict(total, page, size):
    return {"pages": math.ceil(total / size), "total": total, "page": page}


def log_message(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} {message}")


def satoshis(value, decimals):
    return int(float(value) * math.pow(10, decimals))


def amount(value, decimals):
    return round(float(value) / math.pow(10, decimals), decimals)


def dead_response(message="Invalid Request", rid="sync"):
    return {"error": {"code": 404, "message": message}, "id": rid}


async def make_request(method, params=[]):
    settings = get_settings()
    async with aiohttp.ClientSession() as session:
        headers = {"content-type": "text/plain;"}
        data = json.dumps({"id": "sync", "method": method, "params": params})

        try:
            async with session.post(
                settings.general.endpoint, headers=headers, data=data
            ) as r:
                data = await r.json()

                if data["error"]:
                    return data

                return data["result"]

        except Exception:
            return dead_response()
