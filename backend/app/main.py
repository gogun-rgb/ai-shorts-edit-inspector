from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_analysis import router as analysis_router
from app.api.routes_health import router as health_router
from app.core.config import get_settings
from app.core.errors import UserFacingError
from app.services.analysis_service import cleanup_old_analyses, storage_dir


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        storage_dir(settings)
        cleanup_old_analyses(settings)
        yield

    app = FastAPI(
        title="Shorts Edit Inspector API",
        version=settings.app_version,
        description="Local-first rule based short-form video edit inspection API.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(UserFacingError)
    async def user_error_handler(_: Request, exc: UserFacingError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(HTTPException)
    async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    app.include_router(health_router)
    app.include_router(analysis_router)
    return app


app = create_app()
