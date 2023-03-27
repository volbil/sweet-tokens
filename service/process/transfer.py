from ..models import Balance, Transfer, Lock
from ..models import Token, Address, Index
from ..utils import log_message
from .. import constants
from .. import utils

async def process_transfer(decoded, inputs, outputs, block, txid):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    token = await Token.filter(ticker=decoded["ticker"]).first()
    value = utils.amount(decoded["value"], token.decimals)

    send_address = await Address.filter(label=send_address_label).first()
    send_balance = await Balance.filter(
        address=send_address, token=token
    ).first()

    if not (receive_address := await Address.filter(
        label=receive_address_label
    ).first()):
        receive_address = await Address.create(**{
            "label": receive_address_label
        })

    if not (receive_balance := await Balance.filter(
        address=receive_address, token=token
    ).first()):
        receive_balance = await Balance.create(**{
            "address": receive_address,
            "token": token
        })

    has_lock = decoded["lock"] != None

    transfer = await Transfer.create(**{
        "category": constants.CATEGORY_TRANSFER,
        "version": decoded["version"],
        "receiver": receive_address,
        "created": block.created,
        "sender": send_address,
        "has_lock": has_lock,
        "value": value,
        "token": token,
        "block": block,
        "txid": txid
    })

    send_balance.value -= transfer.value
    send_balance.sent += transfer.value

    receive_balance.received += transfer.value

    if has_lock and decoded["lock"] > block.height:
        receive_balance.locked += transfer.value

        await Lock.create(**{
            "unlock_height": decoded["lock"],
            "address": receive_address,
            "value": transfer.value,
            "transfer": transfer,
            "token": token
        })

    else:
        receive_balance.value += transfer.value

    await receive_balance.save()
    await send_balance.save()

    await Index.create(**{
        "category": constants.CATEGORY_TRANSFER,
        "created": block.created,
        "address": send_address,
        "transfer": transfer,
        "token": token
    })

    await Index.create(**{
        "category": constants.CATEGORY_TRANSFER,
        "address": receive_address,
        "created": block.created,
        "transfer": transfer,
        "token": token
    })

    log_message(f"Transfered {value} {token.ticker}")
