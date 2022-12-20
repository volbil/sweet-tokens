from ..models import Token, Balance, Address
from ..utils import log_message
from .. import constants
from .. import utils

def admin(send_address_label, height):
    if not send_address_label in constants.ADMIN_ADDRESSES:
        log_message(f"Address {send_address_label} not in admin list")
        return False

    if constants.ADMIN_ADDRESSES[send_address_label][0] > height:
        log_message(f"Address {send_address_label} not yet admin")
        return False

    if constants.ADMIN_ADDRESSES[
        send_address_label
    ][1] and constants.ADMIN_ADDRESSES[
        send_address_label
    ][1] < height:
        log_message(f"Address {send_address_label} not admin anymore")
        return False

    return True

def value(value):
    if value < constants.MIN_VALUE or value > constants.MAX_VALUE:
        log_message(f"Value {value} not met constraints")
        return False

    return True

def decimals(decimals):
    if decimals < constants.MIN_DECIMALS or decimals > constants.MAX_DECIMALS:
        log_message(f"Decimals {decimals} not met constraints")
        return False

    return True

async def ticker(ticker):
    if len(
        ticker
    ) < constants.MIN_TICKER_LENGTH or len(
        ticker
    ) > constants.MAX_TICKER_LENGTH:
        log_message(f"Ticker {ticker} not met constraints")
        return False

    if await Token.filter(ticker=ticker).first():
        log_message(f"Token with {ticker} already exists")
        return False

    return True

async def token(ticker):
    if not await Token.filter(ticker=ticker).first():
        log_message(f"Token with {ticker} don't exists")
        return False

    return True

async def owner(ticker, owner_address):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with {ticker} don't exists")
        return False

    owner = await token.owner

    if owner.label != owner_address:
        log_message(f"Address {owner_address} is not owner of {ticker}")
        return False

    return True

async def reissuable(ticker):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with {ticker} don't exists")
        return False
    
    return token.reissuable

async def supply_create(value, decimals):
    value = utils.amount(value, decimals)
    if value > constants.MAX_SUPPLY:
        log_message(f"Supply {value} not met constraint")
        return False

    return True

async def supply_issue(ticker, value):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with {ticker} don't exists")
        return False

    value = utils.amount(value, token.decimals)

    if float(token.supply) + value > constants.MAX_SUPPLY:
        log_message(f"Supply issue {value} not met constraint")
        return False

    return True

async def balance(ticker, address_label, value):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with {ticker} don't exists")
        return False

    if not (address := await Address.filter(label=address_label).first()):
        log_message(f"Address {address_label} not found")
        return False

    if address.banned:
        log_message(f"Address {address_label} banned")
        return False

    if not (balance := await Balance.filter(
        address=address, token=token
    ).first()):
        log_message(f"Can't find {ticker} balance for {address_label}")
        return False

    value = utils.amount(value, token.decimals)

    if float(balance.value) - value < 0:
        log_message(f"Address {address_label} don't have {value} {ticker}")
        return False

    return True
