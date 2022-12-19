from fastapi import APIRouter
from .args import BuildArgs
from ..errors import Abort
from .. import utils

router = APIRouter()

@router.post("/construct")
async def construct(args: BuildArgs):
    validate = await utils.make_request("validateaddress", [
        args.send_address
    ])

    if "error" in validate:
        raise Abort("construct", "bad-address")

    if not validate["isvalid"]:
        raise Abort("construct", "bad-address")

    if args.receive_address:
        validate = await utils.make_request("validateaddress", [
            args.receive_address
        ])

        if "error" in validate:
            raise Abort("construct", "bad-address")

        if not validate["isvalid"]:
            raise Abort("construct", "bad-address")

    utxo_list = await utils.make_request("getaddressutxos", [{
        "addresses": [args.send_address]
    }])

    if "error" in utxo_list:
        raise Abort("construct", "bad-address")

    required_amount = args.fee

    if args.receive_address:
        required_amount += args.marker

    input_amount = 0
    outputs = {}
    inputs = []

    for utxo in utxo_list:
        inputs.append({
            "vout": utxo["outputIndex"],
            "txid": utxo["txid"]
        })

        input_amount += utxo["satoshis"]

        if input_amount >= required_amount:
            break

    change = input_amount - required_amount - utils.satoshis(args.fee, 4)

    if args.receive_address:
        change -= utils.satoshis(args.marker, 4)

    outputs[args.send_address] = utils.amount(change, 4)
    outputs["data"] = args.payload

    if args.receive_address:
        outputs[args.receive_address] = args.marker

    raw_tx = await utils.make_request("createrawtransaction", [
        inputs, outputs
    ])

    if "error" in raw_tx:
        raise Abort("construct", "failed")

    return {
        "data": raw_tx
    }
