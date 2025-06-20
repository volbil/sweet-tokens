from app.consensus.protocol import Protocol
from fastapi import APIRouter, Query
from app.utils import get_settings
from app.consensus import regex
from app.chain import get_chain
from app.errors import Abort
from app import constants

from .schemas import (
    TransferArgs,
    CreateArgs,
    IssueArgs,
    BurnArgs,
    CostArgs,
)


router = APIRouter(prefix="/message", tags=["Messages"])


@router.get("/categories", summary="Payload categories")
async def categories():
    return {
        "fee_address": constants.FEE_ADDRESS,
        "transfer": constants.TRANSFER,
        "create": constants.CREATE,
        "issue": constants.ISSUE,
        "unban": constants.UNBAN,
        "burn": constants.BURN,
        "cost": constants.COST,
        "ban": constants.BAN,
    }


@router.get("/decode", summary="Decode payload")
async def decode(payload: str = Query(min_length=2)):
    payload_raw = payload[2:]
    return Protocol.decode(payload_raw)


@router.post("/transfer", summary="Encode transfer payload")
async def transfer(args: TransferArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {
                "version": constants.DEFAULT_VERSION,
                "category": constants.TRANSFER,
                "ticker": args.ticker,
                "value": args.value,
                "lock": args.lock,
            }
        )
    }


@router.post("/burn", summary="Encode burn payload")
async def burn(args: BurnArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {
                "version": constants.DEFAULT_VERSION,
                "category": constants.BURN,
                "ticker": args.ticker,
                "value": args.value,
            }
        )
    }


@router.post("/issue", summary="Encode issue payload")
async def issue(args: IssueArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {
                "version": constants.DEFAULT_VERSION,
                "category": constants.ISSUE,
                "value": args.value,
                "ticker": args.ticker,
            }
        )
    }


@router.post("/create", summary="Encode create payload")
async def create(args: CreateArgs):
    if not regex.ticker(args.ticker)["valid"]:
        raise Abort("token", "invalid-ticker")

    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {
                "version": constants.DEFAULT_VERSION,
                "category": constants.CREATE,
                "reissuable": args.reissuable,
                "decimals": args.decimals,
                "value": args.value,
                "ticker": args.ticker,
            }
        )
    }


@router.post("/ban", summary="Encode ban payload")
async def ban():
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {"version": constants.DEFAULT_VERSION, "category": constants.BAN}
        )
    }


@router.post("/unban", summary="Encode unban payload")
async def unban():
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {"version": constants.DEFAULT_VERSION, "category": constants.UNBAN}
        )
    }


@router.post("/fee", summary="Encode fee address payload")
async def fee():
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {
                "version": constants.DEFAULT_VERSION,
                "category": constants.FEE_ADDRESS,
            }
        )
    }


@router.post("/cost", summary="Encode cost payload")
async def cost(args: CostArgs):
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    return {
        "data": chain["id"]
        + Protocol.encode(
            {
                "version": constants.DEFAULT_VERSION,
                "category": constants.COST,
                "action": args.action,
                "value": args.value,
                "type": args.type,
            }
        )
    }
