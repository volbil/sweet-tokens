from decimal import Decimal
import aiohttp
import config
import json
import math

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
