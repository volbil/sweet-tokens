from ..models import Token, Address, Index
from ..models import Balance, Transfer
from ..utils import log_message
from .. import constants
from .. import utils

async def process_create(decoded, inputs, block, txid):
    send_address = list(inputs)[0]

    value = utils.amount(decoded["value"], decoded["decimals"])

    if not (address := await Address.filter(
        label=send_address
    ).first()):
        address = await Address.create(**{
            "label": send_address
        })

    token = await Token.create(**{
        "reissuable": decoded["reissuable"],
        "decimals": decoded["decimals"],
        "ticker": decoded["ticker"],
        "created": block.created,
        "owner": address,
        "supply": value
    })

    if not (balance := await Balance.filter(
        address=address, token=token
    ).first()):
        balance = await Balance.create(**{
            "address": address,
            "token": token
        })

    transfer = await Transfer.create(**{
        "category": constants.CATEGORY_CREATE,
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

    await Index.create(**{
        "category": constants.CATEGORY_CREATE,
        "created": block.created,
        "transfer": transfer,
        "address": address,
        "token": token
    })

    log_message(f"Created {value} {token.ticker}")
