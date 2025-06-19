from app.utils import make_request, get_settings, amount
from app.chain import get_chain
from .schemas import BuildArgs
from fastapi import APIRouter
from app.errors import Abort


router = APIRouter(tags=["Construct"])


@router.post("/construct", summary="Build token layer transaction")
async def construct(args: BuildArgs):
    validate = await make_request("validateaddress", [args.send_address])

    if "error" in validate:
        raise Abort("construct", "bad-address")

    if not validate["isvalid"]:
        raise Abort("construct", "bad-address")

    if args.receive_address:
        validate = await make_request("validateaddress", [args.receive_address])

        if "error" in validate:
            raise Abort("construct", "bad-address")

        if not validate["isvalid"]:
            raise Abort("construct", "bad-address")

    utxo_list = await make_request(
        "getaddressutxos", [{"addresses": [args.send_address]}]
    )

    if "error" in utxo_list:
        raise Abort("construct", "bad-address")

    required_amount = args.fee

    if args.receive_address:
        required_amount += args.marker

    input_amount = 0
    outputs = {}
    inputs = []

    for utxo in utxo_list:
        inputs.append({"vout": utxo["outputIndex"], "txid": utxo["txid"]})

        input_amount += utxo["satoshis"]

        if input_amount >= required_amount:
            break

    change = input_amount - required_amount - args.fee

    if args.receive_address:
        change -= args.marker

    settings = get_settings()
    chain = get_chain(settings.general.chain)

    outputs[args.send_address] = amount(change, chain["decimals"])

    outputs["data"] = args.payload

    if args.receive_address:
        outputs[args.receive_address] = amount(args.marker, chain["decimals"])

    raw_tx = await make_request("createrawtransaction", [inputs, outputs])

    if "error" in raw_tx:
        raise Abort("construct", "failed")

    return {"data": raw_tx}
