from tortoise.transactions import atomic
from ..parse import parse_transaction
from .decoded import process_decoded
from ..protocol import Protocol
from ..chain import get_chain
from ..models import Block
from .. import utils
import config

@atomic()
async def process_block(data):
    chain = get_chain(config.chain)

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
