from contextlib import asynccontextmanager

import strawberry
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from strawberry.fastapi import GraphQLRouter

from src.config import settings
from src.core.database import engine, get_db
from src.core.dataloaders import Loaders
from src.core.logging import configure_logging, logger
from src.core.security import (
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
    get_cors_origins,
    limiter,
)
from src.features.users.graphql import UserMutation, UserQuery


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    configure_logging()
    logger.info("application_starting", environment=settings.ENVIRONMENT)

    yield

    await engine.dispose()
    logger.info("application_stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, include_in_schema=False)

    # GraphQL Schema dengan error handling
    schema = strawberry.Schema(
        query=UserQuery,
        mutation=UserMutation,
        types=[],  # Daftarkan error types di sini jika perlu
    )

    # Context dengan DataLoader
    async def get_context(request: Request, session=Depends(get_db)):
        return {
            "session": session,
            "loaders": Loaders(session),
            "request": request,
            "logger": logger.bind(request_id=id(request)),
        }

    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="apollo-sandbox" if settings.DEBUG else None,
    )

    app.include_router(graphql_app, prefix="/graphql")

    @app.get("/")
    @limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/minute")
    async def root(request: Request):
        return {
            "app": settings.APP_NAME,
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "docs": "/graphql",
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy", "environment": settings.ENVIRONMENT}

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )

    return app


app = create_app()
