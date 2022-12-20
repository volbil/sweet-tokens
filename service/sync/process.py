from ..models import Block, Token, Address
from tortoise.transactions import atomic
from ..models import Balance, Transfer
from .parse import parse_transaction
from ..protocol import Protocol
from ..models import Ban, Unban
from ..utils import log_message
from .. import constants
from .. import consensus
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

    log_message(f"Created {value} {token.ticker}")

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

    transfer = await Transfer.create(**{
        "category": constants.CATEGORY_TRANSFER,
        "receiver": receive_address,
        "created": block.created,
        "send": send_address,
        "value": value,
        "token": token,
        "block": block,
        "txid": txid
    })

    send_balance.value -= transfer.value
    send_balance.sent += transfer.value

    receive_balance.received += transfer.value
    receive_balance.value += transfer.value

    await receive_balance.save()
    await send_balance.save()

    log_message(f"Transfered {value} {token.ticker}")

async def process_ban(inputs, outputs, block, txid):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    send_address = await Address.filter(label=send_address_label).first()

    if not (receive_address := await Address.filter(
        label=receive_address_label
    ).first()):
        receive_address = await Address.create(**{
            "label": receive_address_label
        })

    await Ban.create(**{
        "address": receive_address,
        "admin": send_address,
        "block": block,
        "txid": txid
    })

    receive_address.banned = True
    await receive_address.save()

    admin = send_address_label
    banned = send_address_label

    log_message(f"Address {banned} banned by {admin}")

async def process_unban(inputs, outputs, block, txid):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    send_address = await Address.filter(label=send_address_label).first()

    if not (receive_address := await Address.filter(
        label=receive_address_label
    ).first()):
        receive_address = await Address.create(**{
            "label": receive_address_label
        })

    await Unban.create(**{
        "address": receive_address,
        "admin": send_address,
        "block": block,
        "txid": txid
    })

    receive_address.banned = False
    await receive_address.save()

    admin = send_address_label
    banned = send_address_label

    log_message(f"Address {banned} unbanned by {admin}")

@atomic()
async def process_decoded(
    decoded, inputs, outputs, block, txid
):
    category = decoded["category"]
    valid = True

    if category == constants.CREATE:
        # Validate create payload
        if await consensus.validate_create(
            decoded, inputs, block.height
        ):
            await process_create(
                decoded, inputs, block, txid
            )

    if category == constants.ISSUE:
        # Validate issue payload
        if await consensus.validate_issue(
            decoded, inputs, block.height
        ):
            await process_issue(
                decoded, inputs, block, txid
            )

    if category == constants.TRANSFER:
        # Validate issue payload
        if await consensus.validate_transfer(
            decoded, inputs, outputs
        ):
            await process_transfer(
                decoded, inputs, outputs, block, txid
            )

    if category == constants.BAN:
        if await consensus.validate_admin(inputs, outputs, block.height):
            await process_ban(
                inputs, outputs, block, txid
            )

    if category == constants.UNBAN:
        if await consensus.validate_admin(inputs, outputs, block.height):
            await process_unban(
                inputs, outputs, block, txid
            )

    return valid

@atomic()
async def process_block(data):
    block = await Block.create(**{
        "created": data["block"]["created"],
        "height": data["block"]["height"],
        "hash": data["block"]["hash"]
    })

    for index, tx_data in enumerate(data["transactions"]):
        txid = tx_data["hash"]
        decoded = None
        outputs = {}
        inputs = {}

        if index == 0:
            continue

        for input in tx_data["inputs"]:
            input_tx_data = await parse_transaction(input["output_txid"])
            input_output = input_tx_data["outputs"][input["output_index"]]

            if input_output["address"]:
                if input_output["address"] not in inputs:
                    inputs[input_output["address"]] = 0

                inputs[input_output["address"]] += utils.satoshis(
                    input_output["value"], constants.NETWORK_DECIMALS
                )

        for output in tx_data["outputs"]:
            if output["script_type"] == "nulldata":
                payload = output["script_hex"][4:]
                decoded = Protocol.decode(payload)

            if output["address"]:
                if output["address"] not in outputs:
                    outputs[output["address"]] = 0

                outputs[output["address"]] += utils.satoshis(
                    output["value"], constants.NETWORK_DECIMALS
                )

        if decoded:
            await process_decoded(decoded, inputs, outputs, block, txid)

@atomic()
async def process_reorg(block):
    await block.delete()
