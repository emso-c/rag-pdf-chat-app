"""
This module acts as the entry point and initializes th FastAPI application a with various middlewares, routers, and configurations.
It also sets up a rate limiter using Redis and serves static files.
"""

from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from app.connection import redis_connection
from app.dependencies import load_route_dependencies
from app.middlewares import (
    ErrorHandler,
    MockAuthMiddleware,
    NotFoundMiddleware,
    LoggingMiddleware,
)
from app.config import app_config
from app.routes import chat, document, history
from app.utils import init_dirs
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import logging

# disable uvicorn logging to use the custom logger
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# initialize directories
init_dirs(
    app_config.chroma_path,
    app_config.history_path,
    app_config.tmp_path,
    app_config.pdf_path,
    app_config.log_path,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Asynchronous context manager for setting up and tearing down application lifespan events.
    """

    # set up limiter
    if not app_config.is_testing:
        await FastAPILimiter.init(redis_connection)

    yield
    if not app_config.is_testing:
        await FastAPILimiter.close()  # closes the redis connection


app = FastAPI(
    title="PDF Chatting Application",
    summary="Allows users to interact with uploaded PDF files.",
    lifespan=lifespan
)


# add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(NotFoundMiddleware)
app.add_middleware(MockAuthMiddleware)
app.add_exception_handler(
    StarletteHTTPException, ErrorHandler.http_exception_handler
)
app.middleware("http")(ErrorHandler.exception_handling_middleware)
app.add_middleware(LoggingMiddleware)

# include routers
base_router = APIRouter(prefix=f"/{app_config.api_version}")
base_router.include_router(router=document.router)
base_router.include_router(router=chat.router)
base_router.include_router(router=history.router)
app.include_router(base_router)


@app.get("/ping", dependencies=load_route_dependencies("ping"))
async def ping():
    with open("test.txt", "a+") as f:
        f.write("A\n")
    return "pong"


# serve static PDFs
app.mount("/static", StaticFiles(directory=app_config.pdf_path), name="static")
