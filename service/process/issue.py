from ..models import Balance, Transfer
from ..models import Token, Address
from ..utils import log_message
from .. import constants
from .. import utils

async def process_issue(decoded, inputs, block, txid):
    send_address = list(inputs)[0]

    token = await Token.filter(ticker=decoded["ticker"]).first()

    value = utils.amount(decoded["value"], token.decimals)

    if not (address := await Address.filter(
        label=send_address
    ).first()):
        address = await Address.create(**{
            "label": send_address
        })

    if not (balance := await Balance.filter(
        address=address, token=token
    ).first()):
        balance = await Balance.create(**{
            "address": address,
            "token": token
        })

    transfer = await Transfer.create(**{
        "category": constants.CATEGORY_ISSUE,
        "created": block.created,
        "receiver": address,
        "value": value,
        "token": token,
        "block": block,
        "txid": txid
    })

    balance.received += transfer.value
    balance.value += transfer.value

    await balance.save()

    token.supply += transfer.value
    await token.save()

    log_message(f"Issued {value} {token.ticker}")
