"""
Module defining a mock authentication middleware for FastAPI.

This middleware extracts an authentication token from incoming requests
and makes it available in the request state. It allows for easy access
to the token in subsequent request handlers.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from fastapi import Request


class MockAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to extract a mock authentication token from request headers.

    This middleware checks for an 'x-token' header in the incoming request,
    stores the token in the request state, and then proceeds with the
    request handling.

    Methods:
        dispatch: Processes the request, extracts the token, and calls
        the next middleware or endpoint.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        token = request.headers.get("x-token")
        request.state.token = token

        response = await call_next(request)
        return response
