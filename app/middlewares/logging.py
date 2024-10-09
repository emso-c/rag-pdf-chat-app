"""
Module defining a logging middleware for FastAPI.

This middleware logs the details of each incoming request and its corresponding
response status. It distinguishes between successful and error responses for
better visibility and debugging.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request and response information.

    This middleware captures the host, request method, URL, HTTP version,
    and response status code for every incoming request. It logs errors
    for unsuccessful responses (4xx and 5xx status codes).

    Methods:
        dispatch: Processes the request and logs the relevant details.
    """

    async def dispatch(self, request: Request, call_next):

        response: Response = await call_next(request)

        log = logger.info
        if str(response.status_code)[0] in ["4", "5"]:  # 4xx, 5xx
            log = logger.error

        log(
            f"{request.headers.get('host')} - {request.method} {request.url} HTTP/{request.scope.get("http_version")} - Response {response.status_code}"
        )

        return response
