from tortoise.contrib.fastapi import register_tortoise
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import fastapi.openapi.utils as fu
from fastapi import FastAPI
from . import errors
import config

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

    register_tortoise(
        app,
        db_url=config.tortoise["db_url"],
        modules=config.tortoise["modules"],
        add_exception_handlers=True,
        generate_schemas=True,
    )

    return app
