from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_session
from app.errors import Abort
from app.layer import service


async def require_token(ticker: str, session: AsyncSession = Depends(get_session)):
    token = await service.get_token(session, ticker)
    if not token:
        raise Abort("token", "not-found")

    return token


async def optional_address(label: str, session: AsyncSession = Depends(get_session)):
    return await service.get_address(session, label)
