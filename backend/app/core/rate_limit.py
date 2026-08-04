"""
Redis-backed rate limiting for FastAPI endpoints.

Uses a sliding window counter keyed by client IP address.
"""

import logging
import time

import redis.asyncio as aioredis
from fastapi import HTTPException, Request, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


async def _get_redis() -> aioredis.Redis:
    """Lazy-initialize a shared async Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
        )
    return _redis_client


def _get_client_ip(request: Request) -> str:
    """Extract the client IP, respecting X-Forwarded-For behind a proxy."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(max_requests: int, window_seconds: int = 60):
    """FastAPI dependency factory for rate limiting.

    Usage:
        @router.post("/login", dependencies=[Depends(rate_limit(5, 60))])
    """

    async def _check_rate_limit(request: Request):
        ip = _get_client_ip(request)
        key = f"rate_limit:{request.url.path}:{ip}"

        try:
            r = await _get_redis()
            now = time.time()
            window_start = now - window_seconds

            pipe = r.pipeline()
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count requests in current window
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(now): now})
            # Set expiry on the key
            pipe.expire(key, window_seconds)
            results = await pipe.execute()

            request_count = results[1]

            if request_count >= max_requests:
                logger.warning(
                    "Rate limit exceeded for %s on %s (%d/%d)", ip, request.url.path, request_count, max_requests
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(window_seconds)},
                )
        except HTTPException:
            raise
        except Exception as exc:
            # If Redis is down, allow the request (fail-open)
            logger.warning("Rate limiter Redis error (failing open): %s", exc)

    return _check_rate_limit
