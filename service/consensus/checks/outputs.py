from service.utils import log_message

def outputs_len(outputs):
    if len(outputs) != 2:
        log_message("Outputs length missmatch")
        return False

    return True
