from service.models import FeeAddress, TokenCost
from service.utils import log_message
from service.chain import get_chain
from decimal import Decimal
from service import utils
from .. import regex
import config

async def token_fee(address, value, ticker, action):
    fee_address = await FeeAddress.filter().order_by("-height").first()

    if fee_address.label != address:
        log_message(f"Invalid fee address {address}")
        return False

    ticker_data = regex.ticker(ticker)

    token_cost = await TokenCost.filter(
        action=action, type=ticker_data["type"]
    ).order_by("-height").first()

    chain = get_chain(config.chain)
    fee = Decimal(utils.amount(value, chain["decimals"]))

    if fee < token_cost.value:
        log_message(f"Fee {float(fee)} is not enough to {action} token")
        return False

    return True
