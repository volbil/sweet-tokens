from .dependencies import validate_build_args
from fastapi import APIRouter, Depends
from app.utils import make_request
from app.construct import service
from .schemas import BuildArgs
from app.errors import Abort


router = APIRouter(tags=["Construct"])


@router.post("/construct", summary="Build token layer transaction")
async def construct(args: BuildArgs = Depends(validate_build_args)):
    utxo_list = await make_request(
        "getaddressutxos", [{"addresses": [args.send_address]}]
    )

    if "error" in utxo_list:
        raise Abort("construct", "bad-address")

    raw_tx = await service.construct(args, utxo_list)

    if "error" in raw_tx:
        raise Abort("construct", "failed")

    return {"data": raw_tx}
