from service.utils import log_message
import copy

def receiver(inputs, outputs):
    send_address = list(inputs)[0]

    if send_address not in outputs:
        return None

    outputs_shallow = copy.copy(outputs)
    outputs_shallow.pop(send_address)

    if len(outputs_shallow) != 1:
        log_message("More than one receiver")
        return None

    return list(outputs_shallow)[0]
