from .. import checks

async def validate_admin(inputs, outputs, height):
    if not checks.inputs_len(inputs):
        return False

    if not checks.outputs_len(outputs):
        return False

    if not checks.receiver(inputs, outputs):
        return False

    send_address = list(inputs)[0]

    # Check if transaction has been sent from admin address
    if not checks.admin(send_address, height):
        return False

    return True

async def validate_admin_ban(inputs, outputs, height, action_ban):
    if not await validate_admin(inputs, outputs, height):
        return False

    if not (receive_address := checks.receiver(inputs, outputs)):
        return False

    # Make sure we don't ban admin address
    if checks.admin(receive_address, height):
        return False

    # Don't ban/unban if we don't need to
    if await checks.banned(receive_address) == action_ban:
        return False

    return True
