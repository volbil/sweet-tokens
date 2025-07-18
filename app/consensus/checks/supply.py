from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import log_message
from sqlalchemy import select
from app.models import Token
from app import constants
from app import utils


async def supply_create(value, decimals):
    supply = utils.amount(value, decimals)
    if supply > constants.MAX_SUPPLY:
        log_message(f"Supply {supply} not met constraint")
        return False

    return True


async def supply_issue(session: AsyncSession, ticker, value):
    if not (
        token := await session.scalar(
            select(Token).filter(Token.ticker == ticker)
        )
    ):
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    value = utils.amount(value, token.decimals)

    if float(token.supply) + value > constants.MAX_SUPPLY:
        log_message(f"Supply issue {value} not met constraint")
        return False

    return True
