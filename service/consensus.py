from .models import Token

ADMIN_ADDRESSES = {
    "rmbc1qlduvy4qs5qumemkuewe5huecgunxlsuw5vgsk6": 0
}

MIN_DECIMALS = 0
MAX_DECIMALS = 8

MIN_TICKER_LENGTH = 3
MAX_TICKER_LENGTH = 8

MIN_VALUE = 1
MAX_VALUE = 10000000000000000000

async def check_admin(send_address, height):
    if not send_address in ADMIN_ADDRESSES:
        return False

    if ADMIN_ADDRESSES[send_address] < height:
        return False

    return True

async def check_value(value):
    if value < MIN_VALUE or value > MAX_VALUE:
        return False

    return True

async def check_decimals(decimals):
    if decimals < MIN_DECIMALS or decimals > MAX_DECIMALS:
        return False

    return True

async def check_ticker(ticker):
    if len(ticker) < MIN_TICKER_LENGTH or len(ticker) > MAX_TICKER_LENGTH:
        return False

    if await Token.filter(ticker=ticker).first():
        return False

    return True
