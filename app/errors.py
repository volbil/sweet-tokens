from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import Request


class ErrorResponse(BaseModel):
    message: str = Field(example="Example error message")
    code: str = Field(example="example_error")


errors = {
    "construct": {
        "failed": ["Failed to build transaction", 400],
        "bad-address": ["Bad address", 400],
    },
    "token": {
        "invalid-ticker": ["Invalid ticker", 400],
        "not-found": ["Token not found", 404],
    },
    "transfer": {"not-found": ["Transfer not found", 404]},
}


class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message


def build_error_code(scope: str, message: str):
    return scope.replace("-", "_") + ":" + message.replace("-", "_")


async def abort_handler(_: Request, exception: Abort):
    error_code = build_error_code(exception.scope, exception.message)

    try:
        error_message = errors[exception.scope][exception.message][0]
        status_code = errors[exception.scope][exception.message][1]
    except Exception:
        error_message = "Unknown error"
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={
            "message": error_message,
            "code": error_code,
        },
    )


async def validation_handler(_: Request, exception: RequestValidationError):
    error = exception.errors()[0]

    field_location = error["loc"][0]
    error_message = f"in request {field_location}"

    if len(error["loc"]) > 1:
        field_name = error["loc"][1]
        error_message = f"{field_name} {error_message}"

    error_message = f"Invalid field {error_message}"

    return JSONResponse(
        status_code=400,
        content={
            "code": "system:validation_error",
            "message": error_message.capitalize(),
        },
    )
