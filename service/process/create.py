from ..models import Token, Address, Index
from ..models import Balance, Transfer
from ..utils import log_message
from ..consensus import regex
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

    ticker_data = regex.ticker(decoded["ticker"])

    token = await Token.create(**{
        "reissuable": decoded["reissuable"],
        "decimals": decoded["decimals"],
        "ticker": decoded["ticker"],
        "type": ticker_data["type"],
        "created": block.created,
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
        "version": decoded["version"],
        "created": block.created,
        "receiver": address,
        "has_lock": False,
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

    need_owner = [constants.TOKEN_ROOT, constants.TOKEN_SUB]

    if ticker_data["type"] in need_owner and token.reissuable:
        token_owner = await Token.create(**{
            "ticker": token.ticker + constants.FLAG_OWNER,
            "type": constants.TOKEN_OWNER,
            "created": block.created,
            "reissuable": False,
            "decimals": 0,
            "supply": 1
        })

        if not (balance_owner := await Balance.filter(
            address=address, token=token_owner
        ).first()):
            balance_owner = await Balance.create(**{
                "token": token_owner,
                "address": address
            })

        transfer_owner = await Transfer.create(**{
            "category": constants.CATEGORY_CREATE,
            "version": decoded["version"],
            "created": block.created,
            "token": token_owner,
            "receiver": address,
            "has_lock": False,
            "block": block,
            "txid": txid,
            "value": 1
        })

        balance_owner.received += transfer_owner.value
        balance_owner.value += transfer_owner.value

        await balance_owner.save()

        await Index.create(**{
            "category": constants.CATEGORY_CREATE,
            "transfer": transfer_owner,
            "created": block.created,
            "token": token_owner,
            "address": address,
        })

        log_message(f"Created owner token {token_owner.ticker}")
