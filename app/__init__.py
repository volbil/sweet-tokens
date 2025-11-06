from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.database import sessionmanager
import fastapi.openapi.utils as fu
from app.utils import get_settings
from fastapi import FastAPI
from app import constants
from app import errors


def create_app(init_db: bool = True) -> FastAPI:
    settings = get_settings()
    lifespan = None

    # SQLAlchemy initialization process
    if init_db:
        sessionmanager.init(settings.database.endpoint)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    fu.validation_error_response_definition = errors.ErrorResponse.model_json_schema()

    app = FastAPI(
        title="Sweet Tokens",
        version=constants.VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(errors.Abort, errors.abort_handler)
    app.add_exception_handler(
        RequestValidationError,
        errors.validation_handler,
    )

    from .construct import router as construct_router
    from .message import router as message_router
    from .system import router as system_router
    from .layer import router as layer_router

    app.include_router(construct_router)
    app.include_router(message_router)
    app.include_router(system_router)
    app.include_router(layer_router)

    return app
