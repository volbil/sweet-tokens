from tortoise.transactions import atomic
from ..parse import parse_transaction
from .decoded import process_decoded
from ..protocol import Protocol
from ..models import Block
from .. import constants
from .. import utils

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
