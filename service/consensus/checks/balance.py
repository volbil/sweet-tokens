from service.models import Token, Address, Balance
from service.utils import log_message
from service import utils

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
