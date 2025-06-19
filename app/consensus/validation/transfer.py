from sqlalchemy.ext.asyncio import AsyncSession
from app.consensus import checks


async def validate_transfer(
    session: AsyncSession, decoded, inputs, outputs, height
):
    if decoded["lock"] and decoded["lock"] <= height:
        return False

    if not checks.inputs_len(inputs):
        return False

    if not checks.outputs_len(outputs):
        return False

    if not checks.receiver(inputs, outputs):
        return False

    send_address = list(inputs)[0]

    # Check transfer value
    if not checks.value(decoded["value"]):
        return False

    # Check if token exists
    if not await checks.token(session, decoded["ticker"]):
        return False

    # Check if address has enough balance
    if not await checks.balance(
        session, decoded["ticker"], send_address, decoded["value"]
    ):
        return False

    return True
