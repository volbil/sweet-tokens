from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Token, Address, Balance
from app.utils import log_message, amount
from sqlalchemy import select


async def balance(session: AsyncSession, ticker, address_label, value):
    if not (
        token := await session.scalar(
            select(Token).filter(Token.ticker == ticker)
        )
    ):
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    if not (
        address := await session.scalar(
            select(Address).filter(Address.label == address_label)
        )
    ):
        log_message(f"Address {address_label} not found")
        return False

    if address.banned:
        log_message(f"Address {address_label} banned")
        return False

    if not (
        balance := await session.scalar(
            select(Balance).filter(
                Balance.address == address, Balance.token == token
            )
        )
    ):
        log_message(f"Can't find {ticker} balance for {address_label}")
        return False

    value = amount(value, token.decimals)

    if float(balance.value) - value < 0:
        log_message(f"Address {address_label} don't have {value} {ticker}")
        return False

    return True
