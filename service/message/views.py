from fastapi import APIRouter, Query
from ..protocol import Protocol
from .args import TransferArgs
from ..consensus import regex
from ..chain import get_chain
from .args import CreateArgs
from .args import IssueArgs
from .args import BurnArgs
from ..errors import Abort
from .. import constants
import config

router = APIRouter(prefix="/message", tags=["Messages"])

@router.get(
    "/categories", summary="Payload categories"
)
async def categories():
    return {
        "transfer": constants.TRANSFER,
        "create": constants.CREATE,
        "issue": constants.ISSUE,
        "unban": constants.UNBAN,
        "burn": constants.BURN,
        "ban": constants.BAN
    }

@router.get(
    "/decode", summary="Decode payload"
)
async def decode(payload: str = Query(min_length=2)):
    payload_raw = payload[2:]
    return Protocol.decode(payload_raw)

@router.post(
    "/transfer", summary="Encode transfer payload"
)
async def transfer(args: TransferArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.TRANSFER,
            "ticker": args.ticker,
            "value": args.value,
            "lock": args.lock
        })
    }

@router.post(
    "/burn", summary="Encode burn payload"
)
async def burn(args: BurnArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.BURN,
            "ticker": args.ticker,
            "value": args.value
        })
    }

@router.post(
    "/issue", summary="Encode issue payload"
)
async def issue(args: IssueArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.ISSUE,
            "value": args.value,
            "ticker": args.ticker
        })
    }

@router.post(
    "/create", summary="Encode create payload"
)
async def create(args: CreateArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.CREATE,
            "reissuable": args.reissuable,
            "decimals": args.decimals,
            "value": args.value,
            "ticker": args.ticker
        })
    }

@router.post(
    "/ban", summary="Encode ban payload"
)
async def ban():
    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.BAN
        })
    }

@router.post(
    "/unban", summary="Encode unban payload"
)
async def unban():
    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.UNBAN
        })
    }
