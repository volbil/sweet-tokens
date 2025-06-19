from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import log_message
from sqlalchemy import select
from app.models import Token


async def reissuable(session: AsyncSession, ticker: str):
    if not (
        token := await session.scalar(
            select(Token).filter(Token.ticker == ticker)
        )
    ):
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    return token.reissuable
