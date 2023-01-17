from fastapi import APIRouter, Depends, Query
from ..protocol import Protocol
from .args import TransferArgs
from ..chain import get_chain
from .args import CreateArgs
from .args import IssueArgs
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
        "ban": constants.BAN
    }

@router.get(
    "/decode", summary="Decode payload"
)
async def decode(payload: str = Query(min_length=2)):
    payload_raw = payload[2:]
    return Protocol.decode(payload_raw)

@router.get(
    "/transfer", summary="Encode transfer payload"
)
async def transfer(args: TransferArgs = Depends()):
    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.TRANSFER,
            "value": args.value,
            "ticker": args.ticker
        })
    }

@router.get(
    "/issue", summary="Encode issue payload"
)
async def issue(args: IssueArgs = Depends()):
    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.ISSUE,
            "value": args.value,
            "ticker": args.ticker
        })
    }

@router.get(
    "/create", summary="Encode create payload"
)
async def create(args: CreateArgs = Depends()):
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

@router.get(
    "/ban", summary="Encode ban payload"
)
async def ban():
    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.BAN
        })
    }

@router.get(
    "/unban", summary="Encode unban payload"
)
async def unban():
    chain = get_chain(config.chain)

    return {
        "data": chain["id"] + Protocol.encode({
            "category": constants.UNBAN
        })
    }
