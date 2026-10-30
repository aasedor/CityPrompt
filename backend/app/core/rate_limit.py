"""Shared, atomic Redis admission limits for authentication and provider quotas."""

import hashlib
import ipaddress
import logging
import uuid
from typing import Awaitable, cast

import redis.asyncio as aioredis
from fastapi import HTTPException, Request

from app.core.config import get_settings

logger = logging.getLogger(__name__)
_redis_client: aioredis.Redis | None = None

# Redis time avoids clock skew between workers. Rejected requests never enlarge
# the set, and UUID members keep simultaneous admissions distinct.
_ADMIT_SCRIPT = """
local t = redis.call('TIME')
local now = tonumber(t[1]) * 1000 + math.floor(tonumber(t[2]) / 1000)
local window = tonumber(ARGV[1]) * 1000
local maximum = tonumber(ARGV[2])
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - window)
if redis.call('ZCARD', KEYS[1]) >= maximum then
    local oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
    return {0, math.max(1, math.ceil((tonumber(oldest[2]) + window - now) / 1000))}
end
redis.call('ZADD', KEYS[1], now, ARGV[3])
redis.call('PEXPIRE', KEYS[1], window)
return {1, 0}
"""


async def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            get_settings().redis_url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2
        )
    return _redis_client


def _get_client_ip(request: Request) -> str:
    """Use the peer unless an explicitly configured proxy supplied the chain."""
    peer = request.client.host if request.client else "unknown"
    configured = getattr(get_settings(), "trusted_proxy_cidrs", "")
    networks = [ipaddress.ip_network(value.strip()) for value in configured.split(",") if value.strip()]
    try:
        address = ipaddress.ip_address(peer)
        if not any(address in network for network in networks):
            return peer
        forwarded = request.headers.get("x-forwarded-for", "")
        if len(forwarded) > 2048:
            return peer
        chain = forwarded.split(",")
        if len(chain) > 20:
            return peer
        hops = [ipaddress.ip_address(value.strip()) for value in chain]
        for hop in reversed(hops):
            if not any(hop in network for network in networks):
                return str(hop)
        return str(hops[0]) if hops else peer
    except ValueError:
        return peer


async def enforce_rate_limit(
    request: Request,
    max_requests: int,
    window_seconds: int = 60,
    *,
    bucket: str | None = None,
    identity: str | None = None,
) -> None:
    """Consume one admission, denying requests when quota storage is unavailable."""
    if max_requests < 1 or window_seconds < 1:
        raise ValueError("Rate limits require positive bounds")
    namespace = bucket or request.url.path
    subject = identity if identity is not None else _get_client_ip(request)
    digest = hashlib.sha256(f"{namespace}\0{subject}".encode()).hexdigest()
    key = f"rate_limit:v2:{digest}"
    try:
        store = await _get_redis()
        # Redis' shared sync/async stubs expose a union; this client is async
        # and this script returns a two-integer array.
        allowed, retry = await cast(
            Awaitable[list[int]],
            store.eval(_ADMIT_SCRIPT, 1, key, str(window_seconds), str(max_requests), uuid.uuid4().hex),
        )
    except Exception:
        # Neither connection strings nor identities belong in operational logs.
        logger.warning("Admission control unavailable")
        raise HTTPException(
            503, "Service temporarily unavailable. Please try again shortly.", headers={"Retry-After": "5"}
        ) from None
    if not allowed:
        raise HTTPException(
            429, "Too many requests. Please try again later.", headers={"Retry-After": str(max(1, int(retry)))}
        )


def rate_limit(max_requests: int, window_seconds: int = 60):
    """FastAPI dependency factory; limits are shared by all application workers."""

    async def _check_rate_limit(request: Request):
        await enforce_rate_limit(request, max_requests, window_seconds)

    return _check_rate_limit
