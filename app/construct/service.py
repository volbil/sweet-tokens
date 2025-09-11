from app.utils import amount, get_settings, make_request
from app.construct.schemas import BuildArgs
from app.chain import get_chain
import typing


async def construct(
    args: BuildArgs, utxo_list: list[dict[str, typing.Any]]
) -> dict[str, str]:
    settings = get_settings()

    required_amount = args.fee
    if args.receive_address:
        required_amount += args.marker

    input_amount = 0
    outputs = {}
    inputs: list[dict[str, str]] = []

    for utxo in utxo_list:
        inputs.append({"vout": utxo["outputIndex"], "txid": utxo["txid"]})

        input_amount += utxo["satoshis"]

        if input_amount >= required_amount:
            break

    change = input_amount - required_amount - args.fee

    if args.receive_address:
        change -= args.marker

    chain = get_chain(settings.general.chain)

    outputs[args.send_address] = amount(change, chain["decimals"])

    outputs["data"] = args.payload

    if args.receive_address:
        outputs[args.receive_address] = amount(args.marker, chain["decimals"])

    raw_tx = await make_request("createrawtransaction", [inputs, outputs])

    return raw_tx
