"""
Module defining middleware for handling 404 Not Found responses.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class NotFoundMiddleware(BaseHTTPMiddleware):
    """Middleware to handle 404 Not Found responses.

    This middleware intercepts requests and checks if the response
    status code is 404. If so, it returns a custom JSON response
    indicating that the requested resource could not be found.

    Methods:
        dispatch: Processes the request and modifies the response
        for 404 status codes.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404:
            return JSONResponse(
                {"detail": "The requested resource could not be found"}, status_code=404
            )
        return response
