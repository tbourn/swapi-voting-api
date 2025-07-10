"""
src.middleware.rate_limit_middleware

================================================================================
Rate Limiting and IP Blocklist Middleware for SWAPI Voting API
================================================================================

Overview
--------
Reusable FastAPI middleware to enforce IP-based rate limiting and blocklist
access control, protecting the SWAPI Voting API from abuse and overload.

Responsibilities
----------------
- Check if the client IP is in a blocklist and deny access if so.
- Track and limit the number of requests per IP within a specified time window.
- Return professional, user-friendly JSON error responses when limits are exceeded.
- Integrate easily with Upstash Redis or similar rate limiting backends.

Configuration
-------------
- `max_requests` (int): Maximum allowed requests per IP in the window.
- `window_seconds` (int): Duration of the rate limiting window in seconds.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.rate_limit_util import increment_rate, is_blocked_ip


class RateLimitAndBlocklistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce IP-based rate limiting and blocklist access control.

    :param app: FastAPI or ASGI application instance.
    :param max_requests: Maximum allowed requests per IP within the window.
    :param window_seconds: Time window duration for rate limiting, in seconds.
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize the middleware with rate limiting parameters.
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        """
        Process each incoming request to enforce blocklist and rate limits.

        :param request: Incoming HTTP request.
        :param call_next: Callable to pass request to the next middleware or route handler.
        :return: HTTP response, either an error if blocked/limited or the downstream response.
        """
        client = request.client
        ip = client.host if client else "unknown"

        if is_blocked_ip(ip):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "ACCESS_DENIED",
                    "detail": (
                        "Your IP address has been blocked due to suspicious activity. "
                        "If you believe this is an error, please contact our support team."
                    ),
                    "support": "mailto:thomas.bournaveas@gmail.com",
                },
            )

        count = increment_rate(ip, limit_window=self.window_seconds)
        if count > self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "detail": (
                        "Too many requests detected from your IP address. "
                        f"Please wait before retrying. Rate limit: {self.max_requests} requests per {self.window_seconds // 60} minutes."
                    ),
                    "help": "https://thomasbournaveas.com/rate-limit-policy",
                },
            )

        return await call_next(request)
