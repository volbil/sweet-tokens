from service.utils import log_message

def inputs_len(inputs):
    if len(inputs) != 1:
        log_message("Inputs length missmatch")
        return False

    return True
