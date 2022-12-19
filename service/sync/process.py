from ..models import Block, Token, Address
from tortoise.transactions import atomic
from ..models import Balance, Transfer
from .parse import parse_transaction
from ..protocol import Protocol
from ..utils import log_message
from .. import constants
from .. import consensus
from .. import utils

@atomic()
async def process_decoded(
    decoded, inputs, outputs, block, txid
):
    if len(inputs) != 1:
        return False

    send_address = list(inputs)[0]
    category = decoded["category"]
    valid = True

    if category == constants.CREATE:
        # Check if transaction has been sent from admin address
        valid = await consensus.check_admin(send_address, block.height)

        # Check value for new token
        valid = await consensus.check_value(decoded["value"])

        # Check decimal points for new token
        valid = await consensus.check_decimals(decoded["decimals"])

        # Check ticker length and if it's available
        valid = await consensus.check_ticker(decoded["ticker"])

        if valid:
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
                "category": constants.TRANSFER_CREATE,
                "created": block.created,
                "value": value,
                "token": token,
                "block": block,
                "txid": txid
            })

            balance.received += transfer.value
            balance.value += transfer.value

            await balance.save()

            log_message(f"Created token {token.ticker}")

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
                payload = output["script_asm"].split(" ")[1]
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
