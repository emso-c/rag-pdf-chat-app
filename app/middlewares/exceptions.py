"""
Module defining error handling for FastAPI applications.

This module provides a centralized way to handle HTTP exceptions and general
errors in the application, logging the errors for debugging and returning
standardized error responses.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.logger import logger


class ErrorHandler:
    """Class for handling errors in a FastAPI application.

    This class includes methods for handling HTTP exceptions and general
    exceptions that may occur during request processing.

    Methods:
        http_exception_handler: Handles HTTP exceptions and logs details.
        exception_handling_middleware: Middleware for catching unhandled exceptions.
    """

    @staticmethod
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(exc.detail)
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)

    @staticmethod
    async def exception_handling_middleware(request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.exception(f"Unhandled exception: {e.__class__.__name__, e}")

            return JSONResponse(
                content={"detail": "Something went wrong"}, status_code=500
            )
