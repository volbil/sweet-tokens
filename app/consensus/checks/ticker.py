from service.utils import log_message
from service.models import Token
from service import constants
from .. import regex

def ticker_type(ticker, reissuable, decimals, value):
    ticker_data = regex.ticker(ticker)

    if ticker_data["type"] == constants.TOKEN_OWNER:
        log_message("Can't create owner token")
        return False

    if ticker_data["type"] == constants.TOKEN_UNIQUE:
        if reissuable:
            log_message("Unique token can't be reissuable")
            return False

        if decimals > 0:
            log_message("Unique token should have 0 decimals")
            return False

        if value != 1:
            log_message("Unique token valube should be 1")
            return False

    return True

async def ticker(ticker):
    ticker_data = regex.ticker(ticker)

    if not ticker_data["valid"]:
        log_message(ticker_data["error"])
        return False

    if await Token.filter(ticker=ticker).first():
        log_message(f"Token with ticker {ticker} already exists")
        return False

    return True
