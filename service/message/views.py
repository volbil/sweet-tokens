from fastapi import APIRouter, Depends
from ..protocol import Protocol
from .args import TransferArgs
from .args import CreateArgs
from .args import IssueArgs
from .. import constants

router = APIRouter(prefix="/message", tags=["Messages"])

@router.get("/categories")
async def categories():
    return {
        "transfer": constants.TRANSFER,
        "create": constants.CREATE,
        "issue": constants.ISSUE,
        "unban": constants.UNBAN,
        "ban": constants.BAN
    }

@router.get("/decode")
async def decode(payload: str):
    return Protocol.decode(payload)

@router.get("/transfer")
async def transfer(args: TransferArgs = Depends()):
    return {
        "data": Protocol.encode({
            "category": constants.TRANSFER,
            "value": args.value,
            "ticker": args.ticker
        })
    }

@router.get("/issue")
async def issue(args: IssueArgs = Depends()):
    return {
        "data": Protocol.encode({
            "category": constants.ISSUE,
            "value": args.value,
            "ticker": args.ticker
        })
    }

@router.get("/create")
async def create(args: CreateArgs = Depends()):
    return {
        "data": Protocol.encode({
            "category": constants.CREATE,
            "reissuable": args.reissuable,
            "decimals": args.decimals,
            "value": args.value,
            "ticker": args.ticker
        })
    }

@router.get("/ban")
async def ban():
    return {
        "data": Protocol.encode({
            "category": constants.BAN
        })
    }

@router.get("/unban")
async def unban():
    return {
        "data": Protocol.encode({
            "category": constants.UNBAN
        })
    }
