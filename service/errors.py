from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import Request

class ErrorResponse(BaseModel):
    message: str = Field(example="Example error message")
    code: str = Field(example="example_error")

errors = {
    "construct": {
        "bad-address": ["Bad address", 400],
        "failed": ["Failed to build transaction", 400],
    },
    "token": {
        "not-found": ["Token not found", 404],
        "invalid-ticker": ["Invalid ticker", 400],
    },
    "transfer": {
        "not-found": ["Transfer not found", 404]
    }
}

class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message

async def abort_handler(request: Request, exc: Abort):
    error_code = exc.scope.replace("-", "_") + "_" + exc.message.replace("-", "_")

    try:
        error_message = errors[exc.scope][exc.message][0]
        status_code = errors[exc.scope][exc.message][1]
    except Exception:
        error_message = "Unknown error"
        status_code = 400

    return JSONResponse(
        content={
            "message": error_message, "code": error_code
        },
        status_code=status_code
    )

async def validation_handler(request: Request, exc: RequestValidationError):
    exc_str = str(exc).replace("\n", " ").replace("   ", " ")
    return JSONResponse(
        content={
            "message": exc_str, "code": "validation_error"
        },
        status_code=422
    )
