from service.utils import log_message
from service.models import Token

async def reissuable(ticker):
    if not (token := await Token.filter(ticker=ticker).first()):
        log_message(f"Token with ticker {ticker} don't exists")
        return False
    
    return token.reissuable
