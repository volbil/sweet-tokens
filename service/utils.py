from datetime import datetime
from decimal import Decimal
import aiohttp
import config
import json
import math

# Helper function for toroise pagination
def pagination(page, size=20):
    limit = size
    offset = (limit * (page)) - limit

    return limit, offset, size

# Helper function to make pagication dict for api
def pagination_dict(total, page, size):
    return {
        "pages": math.ceil(total / size),
        "total": total,
        "page": page
    }

def log_message(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} {message}")

def satoshis(value, decimals):
    return int(float(value) * math.pow(10, decimals))

def amount(value, decimals):
    return round(float(value) / math.pow(10, decimals), decimals)

def float_to_Decimal(value):
    return Decimal(str(value))

def dead_response(message="Invalid Request", rid="sync"):
    return {"error": {"code": 404, "message": message}, "id": rid}

async def make_request(method, params=[]):
    async with aiohttp.ClientSession() as session:
        headers = {"content-type": "text/plain;"}
        data = json.dumps({
            "id": "sync", "method": method, "params": params
        })

        try:
            async with session.post(
                config.endpoint, headers=headers, data=data
            ) as r:
                data = await r.json()

                if data["error"]:
                    return data

                return data["result"]

        except Exception:
            return dead_response()
