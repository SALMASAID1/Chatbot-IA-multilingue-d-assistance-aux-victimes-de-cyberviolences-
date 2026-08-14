"""Rate limiting middleware using slowapi.

Provides per-IP rate limiting to prevent abuse of the chat endpoint
while keeping health checks unlimited.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import RATE_LIMIT_CHAT, RATE_LIMIT_ADMIN


# Create the global limiter instance (keyed by client IP)
limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Configure rate limiting middleware on the FastAPI application.

    Rate limits (configurable via environment):
    - /api/chat: 30 requests/minute per IP (default)
    - /api/admin/*: 10 requests/minute per IP (default)
    - /api/health: unlimited
    """
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Trop de requêtes. Veuillez réessayer dans quelques instants.",
                "error_code": "RATE_LIMIT_EXCEEDED",
            },
        )
