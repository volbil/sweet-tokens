from service.utils import log_message
from service.models import Token

async def token(ticker):
    if not await Token.filter(ticker=ticker).first():
        log_message(f"Token with ticker {ticker} don't exists")
        return False

    return True
