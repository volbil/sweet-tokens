from tortoise.contrib.fastapi import register_tortoise
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import fastapi.openapi.utils as fu
from fastapi import FastAPI
from . import constants
from . import errors
import config

def create_app() -> FastAPI:
    fu.validation_error_response_definition = errors.ErrorResponse.schema()

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            version=constants.VERSION,
            title="Token layer",
            routes=app.routes
        )

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app = FastAPI()

    app.openapi = custom_openapi

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
    from .system import system
    from .layer import layer

    app.include_router(construct)
    app.include_router(message)
    app.include_router(system)
    app.include_router(layer)

    register_tortoise(
        app, config=config.tortoise,
        add_exception_handlers=True,
        generate_schemas=True,
    )

    return app
