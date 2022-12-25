from fastapi import APIRouter
from .. import constants

router = APIRouter(tags=["System"])

@router.get(
    "/version", summary="System version"
)
async def layer_version():
    return {
        "version": constants.VERSION
    }
