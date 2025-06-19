from app.models import FeeAddress, TokenCost
from app.utils import get_settings, amount
from app.utils import log_message
from app.chain import get_chain
from app.consensus import regex
from decimal import Decimal


async def token_fee(address, value, ticker, action):
    fee_address = await FeeAddress.filter().order_by("-height").first()

    if fee_address.label != address:
        log_message(f"Invalid fee address {address}")
        return False

    ticker_data = regex.ticker(ticker)

    token_cost = (
        await TokenCost.filter(action=action, type=ticker_data["type"])
        .order_by("-height")
        .first()
    )

    settings = get_settings()
    chain = get_chain(settings.general.chain)
    fee = Decimal(amount(value, chain["decimals"]))

    if fee < token_cost.value:
        log_message(f"Fee {float(fee)} is not enough to {action} token")
        return False

    return True
