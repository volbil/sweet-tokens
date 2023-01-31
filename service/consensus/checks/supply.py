from service.utils import log_message
from service.models import Token
from service import constants
from service import utils

async def supply_create(value, decimals):
    supply = utils.amount(value, decimals)
    if supply > constants.MAX_SUPPLY:
        log_message(f"Supply {supply} not met constraint")
        return False

    return True

async def supply_issue(ticker, value):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    value = utils.amount(value, token.decimals)

    if float(token.supply) + value > constants.MAX_SUPPLY:
        log_message(f"Supply issue {value} not met constraint")
        return False

    return True
