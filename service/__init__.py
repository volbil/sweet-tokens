from tortoise.contrib.fastapi import register_tortoise
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import fastapi.openapi.utils as fu
from fastapi import FastAPI
from . import errors
import config

version = "0.1"

def create_app() -> FastAPI:
    fu.validation_error_response_definition = errors.ErrorResponse.schema()

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, errors.validation_handler)
    app.add_exception_handler(errors.Abort, errors.abort_handler)

    from .construct import construct
    from .message import message
    from .layer import layer

    app.include_router(construct)
    app.include_router(message)
    app.include_router(layer)

    @app.get("/version")
    async def layer_version():
        return {
            "version": version
        }

    register_tortoise(
        app, config=config.tortoise,
        add_exception_handlers=True,
        generate_schemas=True,
    )

    return app
