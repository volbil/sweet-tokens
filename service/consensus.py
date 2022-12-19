from .models import Token
from . import utils

ADMIN_ADDRESSES = {
    "rmbc1qlduvy4qs5qumemkuewe5huecgunxlsuw5vgsk6": 0
}

MIN_DECIMALS = 0
MAX_DECIMALS = 8

MIN_TICKER_LENGTH = 3
MAX_TICKER_LENGTH = 8

MIN_VALUE = 1
MAX_VALUE = 10000000000000000000

MAX_SUPPLY = 100000000000

def check_admin(send_address, height):
    if not send_address in ADMIN_ADDRESSES:
        return False

    if ADMIN_ADDRESSES[send_address] < height:
        return False

    return True

def check_value(value):
    if value < MIN_VALUE or value > MAX_VALUE:
        return False

    return True

def check_decimals(decimals):
    if decimals < MIN_DECIMALS or decimals > MAX_DECIMALS:
        return False

    return True

async def check_ticker(ticker):
    if len(ticker) < MIN_TICKER_LENGTH or len(ticker) > MAX_TICKER_LENGTH:
        return False

    if await Token.filter(ticker=ticker).first():
        return False

    return True

async def check_token(ticker):
    if await Token.filter(ticker=ticker).first():
        return True

    return False

async def check_owner(ticker, owner_address=None):
    if token := await Token.filter(ticker=ticker).first():
        owner = await token.owner

        if owner.label != owner_address:
            return False

        return True

    return False

async def check_reissuable(ticker):
    if token := await Token.filter(ticker=ticker).first():
        return token.reissuable

    return False

async def check_supply_create(value, decimals):
    if utils.amount(value, decimals) > MAX_SUPPLY:
        return False

    return True

async def check_supply_issue(ticker, value):
    if token := await Token.filter(ticker=ticker).first():
        if float(token.supply) + utils.amount(value, token.decimals) > MAX_SUPPLY:
            return False

    return True
