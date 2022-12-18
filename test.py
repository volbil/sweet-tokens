from service.utils import satoshis, amount
from service.utils import make_request
from service.protocol import Protocol
from service.sync import sync_chain
from service import constants
import asyncio

async def test():
    SEND_ADDRESS = "rmbc1qlduvy4qs5qumemkuewe5huecgunxlsuw5vgsk6"
    SEND_KEY = "cUgk364exd5bSCVc78df7HWjGZs6Vs9JK7teAA2RcSnmbB7q2Y4v"

    MARKER = satoshis(0.0001, 4)
    TX_FEE = satoshis(0.015, 4)

    utxos = await make_request("getaddressutxos", [{
        "addresses": [SEND_ADDRESS]
    }])

    inputs = []
    input_amount = 0
    required_amount = TX_FEE + MARKER

    for utxo in utxos:
        inputs.append({
            "vout": utxo["outputIndex"],
            "txid": utxo["txid"]
        })

        input_amount += utxo["satoshis"]

        if input_amount >= required_amount:
            break

    change = input_amount - required_amount

    payload = Protocol.encode({
        "category": constants.CREATE,
        "reissuable": True,
        "decimals": 4,
        "amount": satoshis(1000000, 4),
        "ticker": "TEST"
    })

    outputs = {
        SEND_ADDRESS: amount(change, 4),
        "data": payload
    }

    raw_tx = await make_request("createrawtransaction", [inputs, outputs])

    signed = await make_request("signrawtransactionwithkey", [raw_tx, [SEND_KEY]])

    print(signed["hex"])

if __name__ == "__main__":
    asyncio.run(sync_chain())
    # asyncio.run(test())
