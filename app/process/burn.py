from ..models import Token, Address, Index
from ..models import Balance, Transfer
from ..utils import log_message
from .. import constants
from .. import utils

async def process_burn(decoded, inputs, block, txid):
    send_address_label = list(inputs)[0]

    token = await Token.filter(ticker=decoded["ticker"]).first()
    value = utils.amount(decoded["value"], token.decimals)

    send_address = await Address.filter(label=send_address_label).first()
    send_balance = await Balance.filter(
        address=send_address, token=token
    ).first()

    transfer = await Transfer.create(**{
        "category": constants.CATEGORY_BURN,
        "version": decoded["version"],
        "created": block.created,
        "sender": send_address,
        "has_lock": False,
        "receiver": None,
        "value": value,
        "token": token,
        "block": block,
        "txid": txid
    })

    send_balance.value -= transfer.value
    send_balance.sent += transfer.value
    await send_balance.save()
    
    token.supply -= transfer.value
    await token.save()

    await Index.create(**{
        "category": constants.CATEGORY_BURN,
        "created": block.created,
        "address": send_address,
        "transfer": transfer,
        "token": token
    })

    log_message(f"Burned {value} {token.ticker}")
