from app.utils import make_request
from .schemas import BuildArgs
from app.errors import Abort


async def validate_build_args(args: BuildArgs):
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

    return args
