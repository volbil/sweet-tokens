from service.utils import log_message
from service.models import Token
from service import constants
from .. import regex

async def owner(ticker, owner_address):
    if not await Token.filter(ticker=ticker).first():
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    owner_ticker = ticker + constants.FLAG_OWNER

    if not (token_owner := await Token.filter(ticker=owner_ticker).first()):
        log_message(f"Token with ticker {owner_ticker} don't exists")
        return False

    if not (balance := await token_owner.balances.filter(
        token=token_owner,
        value__gt=0
    ).first()):
        log_message(f"Couldn't find holder of {owner_ticker}")
        return False

    holder = await balance.address

    if holder.label != owner_address:
        log_message(f"Address {owner_address} is not owner of {ticker}")
        return False

    return True

async def owner_parent(ticker, owner_address):
    ticker_data = regex.ticker(ticker)

    if ticker_data["parent"] == None:
        return True

    owner_ticker = ticker_data["parent"] + constants.FLAG_OWNER

    if not (token_owner := await Token.filter(ticker=owner_ticker).first()):
        log_message(f"Token with ticker {owner_ticker} don't exists")
        return False

    if not (balance := await token_owner.balances.filter(
        token=token_owner,
        value__gt=0
    ).first()):
        log_message(f"Couldn't find holder of {owner_ticker}")
        return False

    holder = await balance.address

    if holder.label != owner_address:
        log_message(f"Address {owner_address} is not owner of {ticker}")
        return False

    return True
