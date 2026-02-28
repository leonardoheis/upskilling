from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from upskills.core import get_settings
from upskills.db import DatabaseProvider
from upskills.injections import Container

from .routers import base_router, v1_router


@asynccontextmanager
@inject
async def lifespan(
    _app: FastAPI,
    db_provider: DatabaseProvider = Provide["db_provider"],
) -> AsyncIterator[None]:
    await db_provider.init_db()
    yield
    await db_provider.close()


def app_factory() -> FastAPI:
    settings = get_settings()

    container = Container()
    container.config.from_pydantic(settings)
    container.wire(packages=["upskills"])  # pylint: disable=no-member E1101

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(base_router)
    app.include_router(v1_router)

    return app
