from sqlalchemy.ext.asyncio import AsyncSession
from app.consensus import checks
from app import constants


async def validate_issue(session: AsyncSession, decoded, inputs, outputs):
    if not checks.inputs_len(inputs):
        return False

    if not checks.outputs_len(outputs):
        return False

    if not (receive_address := checks.receiver(inputs, outputs)):
        return False

    send_address = list(inputs)[0]

    # Check value for new tokens issued
    if not checks.value(decoded["value"]):
        return False

    # Check if token reissuable
    if not await checks.reissuable(session, decoded["ticker"]):
        return False

    # Check if token exists
    if not await checks.token(session, decoded["ticker"]):
        return False

    # Check if sender owns token
    if not await checks.owner(session, decoded["ticker"], send_address):
        return False

    # Check if issued amount within supply constraints
    if not await checks.supply_issue(
        session, decoded["ticker"], decoded["value"]
    ):
        return False

    # Check if fee is enough for given action
    if not await checks.token_fee(
        session,
        receive_address,
        outputs[receive_address],
        decoded["ticker"],
        constants.ACTION_ISSUE,
    ):
        return False

    return True
