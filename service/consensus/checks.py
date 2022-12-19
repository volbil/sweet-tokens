from ..models import Token, Balance, Address
from ..utils import log_message
from .. import constants
from .. import utils

ADMIN_ADDRESSES = {
    "rmbc1qlduvy4qs5qumemkuewe5huecgunxlsuw5vgsk6": [0, None]
}

def admin(send_address, height):
    if not send_address in ADMIN_ADDRESSES:
        return False

    if ADMIN_ADDRESSES[send_address][0] > height:
        return False

    if ADMIN_ADDRESSES[
        send_address
    ][1] and ADMIN_ADDRESSES[
        send_address
    ][1] < height:
        return False

    return True

def value(value):
    if value < constants.MIN_VALUE or value > constants.MAX_VALUE:
        return False

    return True

def decimals(decimals):
    if decimals < constants.MIN_DECIMALS or decimals > constants.MAX_DECIMALS:
        return False

    return True

async def ticker(ticker):
    if len(
        ticker
    ) < constants.MIN_TICKER_LENGTH or len(
        ticker
    ) > constants.MAX_TICKER_LENGTH:
        return False

    if await Token.filter(ticker=ticker).first():
        return False

    return True

async def token(ticker):
    if await Token.filter(ticker=ticker).first():
        return True

    return False

async def owner(ticker, owner_address=None):
    if not (token := await Token.filter(ticker=ticker).first()):
        return False

    owner = await token.owner

    if owner.label == owner_address:
        return True

    return False

async def reissuable(ticker):
    if not (token := await Token.filter(ticker=ticker).first()):
        return False
    
    return token.reissuable

async def supply_create(value, decimals):
    if utils.amount(value, decimals) > constants.MAX_SUPPLY:
        return False

    return True

async def supply_issue(ticker, value):
    if not (token := await Token.filter(ticker=ticker).first()):
        return False

    if float(token.supply) + utils.amount(
        value, token.decimals
    ) > constants.MAX_SUPPLY:
        return False

    return True

async def balance(ticker, address_label, value):
    if not (token := await Token.filter(ticker=ticker).first()):
        return False

    if not (address := await Address.filter(label=address_label).first()):
        return False

    if not (balance := await Balance.filter(
        address=address, token=token
    ).first()):
        return False

    amount = utils.amount(value, token.decimals)

    if float(balance.value) - amount < 0:
        return False

    return True
