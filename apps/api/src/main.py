import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.core.config import settings
from src.core.logging import configure_logging
from src.routers.agents import router as agents_router
from src.services.officer_directory import OfficerNotFoundError

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Application startup: environment=%s", settings.environment)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)

if settings.environment == "local":
    # Dev-only: lets the static web test UI (served from a different origin) call the API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(OfficerNotFoundError)
async def officer_not_found_handler(request: Request, exc: OfficerNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": "officer_not_found", "detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"error": "internal_server_error"})


@app.get("/healthz")
@limiter.exempt  # type: ignore[untyped-decorator]
async def healthz(request: Request) -> dict[str, str]:
    return {"status": "ok"}


app.include_router(agents_router)
