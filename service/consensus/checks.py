from ..models import Token, Balance, Address
from ..models import FeeAddress, TokenCost
from ..utils import log_message
from ..chain import get_chain
from decimal import Decimal
from .. import constants
from .. import utils
from . import regex
import config
import copy

def inputs_len(inputs):
    if len(inputs) != 1:
        log_message("Inputs length missmatch")
        return False

    return True

def outputs_len(outputs):
    if len(outputs) != 2:
        log_message("Outputs length missmatch")
        return False

    return True

def receiver(inputs, outputs):
    send_address = list(inputs)[0]

    if send_address not in outputs:
        return None

    outputs_shallow = copy.copy(outputs)
    outputs_shallow.pop(send_address)

    if len(outputs_shallow) != 1:
        log_message("More than one receiver")
        return None

    return list(outputs_shallow)[0]

def admin(send_address_label, height):
    chain = get_chain(config.chain)

    if not send_address_label in chain["admin"]:
        return False

    if chain["admin"][send_address_label][0] > height:
        log_message(f"Address {send_address_label} not yet admin")
        return False

    if chain["admin"][
        send_address_label
    ][1] and chain["admin"][
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

async def token(ticker):
    if not await Token.filter(ticker=ticker).first():
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    return True

async def owner(ticker, owner_address):
    if not await Token.filter(ticker=ticker).first():
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    owner_ticker = ticker + constants.FLAG_OWNER

    if not (token_owner := await Token.filter(ticker=owner_ticker).first()):
        log_message(f"Token with ticker {owner_ticker} don't exists")
        return False

    if not (balance := await token_owner.balances.filter(value__gt=0).first()):
        log_message(f"Couldn't find holder of {owner_ticker}")
        return False

    holder = await balance.address

    if holder.label != owner_address:
        log_message(f"Address {owner_address} is not owner of {ticker}")
        return False

    return True

async def reissuable(ticker):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with ticker {ticker} don't exists")
        return False
    
    return token.reissuable

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

async def balance(ticker, address_label, value):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with ticker {ticker} don't exists")
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

async def banned(address_label):
    if not (address := await Address.filter(label=address_label).first()):
        log_message(f"Address {address_label} not found")
        return False

    return address.banned

async def token_fee(address, value, ticker, action):
    fee_address = await FeeAddress.filter().order_by("-height").first()

    if fee_address.label != address:
        log_message(f"Invalid fee address {address}")
        return False

    ticker_data = regex.ticker(ticker)

    token_cost = await TokenCost.filter(
        action=action, category=ticker_data["type"]
    ).order_by("-height").first()

    chain = get_chain(config.chain)
    fee = Decimal(utils.amount(value, chain["decimals"]))

    if fee < token_cost.value:
        log_message(f"Fee {float(fee)} is not enough to {action} token")
        return False

    return True
