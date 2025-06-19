from sqlalchemy.ext.asyncio import AsyncSession
from app.models import FeeAddress, TokenCost
from app.utils import get_settings, amount
from app.utils import log_message
from app.chain import get_chain
from app.consensus import regex
from sqlalchemy import select
from decimal import Decimal


async def token_fee(session: AsyncSession, address, value, ticker, action):
    fee_address = await session.scalar(
        select(FeeAddress).order_by(FeeAddress.height.desc())
    )

    if fee_address.label != address:
        log_message(f"Invalid fee address {address}")
        return False

    ticker_data = regex.ticker(ticker)

    token_cost = await session.scalar(
        select(TokenCost)
        .filter(
            TokenCost.action == action,
            TokenCost.type == ticker_data["type"],
        )
        .order_by(TokenCost.height.desc())
    )

    settings = get_settings()
    chain = get_chain(settings.general.chain)
    fee = Decimal(amount(value, chain["decimals"]))

    if fee < token_cost.value:
        log_message(f"Fee {float(fee)} is not enough to {action} token")
        return False

    return True
