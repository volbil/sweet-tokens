from ..models import FeeAddress, TokenCost
from tortoise.transactions import atomic
from ..parse import parse_transaction
from .decoded import process_decoded
from ..protocol import Protocol
from ..utils import log_message
from ..chain import get_chain
from ..models import Block
from .. import constants
from .. import utils
import config

SNAP_TXID = "3426ccad3017e14a4ab6efddaa44cb31beca67a86c82f63de18705f1b6de88df"

@atomic()
async def process_block(data):
    chain = get_chain(config.chain)

    block = await Block.create(**{
        "created": data["block"]["created"],
        "height": data["block"]["height"],
        "hash": data["block"]["hash"]
    })

    if block.height == chain["genesis"]["height"]:
        await FeeAddress.create(**{
            "label": chain["cost"]["address"],
            "height": block.height,
            "block": block
        })

        await TokenCost.bulk_create([
            # Create
            TokenCost(**{
                "value": chain["cost"]["create"]["root"],
                "action": constants.ACTION_CREATE,
                "type": constants.TOKEN_ROOT,
                "height": block.height,
                "block": block
            }),
            TokenCost(**{
                "value": chain["cost"]["create"]["sub"],
                "action": constants.ACTION_CREATE,
                "type": constants.TOKEN_SUB,
                "height": block.height,
                "block": block
            }),
            TokenCost(**{
                "value": chain["cost"]["create"]["unique"],
                "action": constants.ACTION_CREATE,
                "type": constants.TOKEN_UNIQUE,
                "height": block.height,
                "block": block
            }),
            # Issue
            TokenCost(**{
                "value": chain["cost"]["issue"]["root"],
                "action": constants.ACTION_ISSUE,
                "type": constants.TOKEN_ROOT,
                "height": block.height,
                "block": block
            }),
            TokenCost(**{
                "value": chain["cost"]["issue"]["sub"],
                "action": constants.ACTION_ISSUE,
                "type": constants.TOKEN_SUB,
                "height": block.height,
                "block": block
            })
        ])

        log_message("Initialized initial cost and fee address")

    for index, tx_data in enumerate(data["transactions"]):
        txid = tx_data["hash"]
        decoded = None
        outputs = {}
        inputs = {}

        if index == 0:
            continue

        for input in tx_data["inputs"]:
            if input["output_txid"] == SNAP_TXID:
                continue

            input_tx_data = await parse_transaction(input["output_txid"])
            input_output = input_tx_data["outputs"][input["output_index"]]

            if input_output["address"]:
                if input_output["address"] not in inputs:
                    inputs[input_output["address"]] = 0

                inputs[input_output["address"]] += utils.satoshis(
                    input_output["value"], chain["decimals"]
                )

        for output in tx_data["outputs"]:
            if output["script_type"] == "nulldata":
                payload = output["script_hex"][4:]

                # Prevent crash with malformed payload
                if len(payload) < 4:
                    continue

                # Check chain id
                chain_id = payload[:2]
                if chain_id != chain["id"]:
                    continue
                
                # Decode payload
                payload_raw = payload[2:]
                decoded = Protocol.decode(payload_raw)

            if output["address"]:
                if output["address"] not in outputs:
                    outputs[output["address"]] = 0

                outputs[output["address"]] += utils.satoshis(
                    output["value"], chain["decimals"]
                )

        if decoded:
            await process_decoded(decoded, inputs, outputs, block, txid)
