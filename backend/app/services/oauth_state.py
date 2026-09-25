"""Short-lived OAuth state, bound to the initiating browser and consumed once."""

import hashlib
import json
import secrets

import redis.asyncio as redis
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from app.core.config import get_settings

STATE_TTL_SECONDS = 600
_CONSUME = """
local value = redis.call('GET', KEYS[1])
if not value then return false end
local record = cjson.decode(value)
if record.binding ~= ARGV[1] then return false end
redis.call('DEL', KEYS[1])
return record.origin
"""


def _client():
    return redis.from_url(get_settings().redis_url, decode_responses=True,
                          socket_connect_timeout=2, socket_timeout=2)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _key(provider: str, state: str) -> str:
    return f"oauth-state:{provider}:{_digest(state)}"


def cookie_name(provider: str) -> str:
    return f"{'__Host-' if get_settings().is_production else ''}cityprompt-oauth-{provider}"


async def issue_state(provider: str, origin: str) -> tuple[str, str]:
    state, binding = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    try:
        async with _client() as client:
            created = await client.set(_key(provider, state), json.dumps({"binding": _digest(binding), "origin": origin}),
                                       ex=STATE_TTL_SECONDS, nx=True)
            if not created:
                raise RuntimeError("Unable to issue a unique sign-in attempt")
    except Exception as exc:
        raise HTTPException(503, "Sign-in is temporarily unavailable. Please try again.") from exc
    return state, binding


def bind_browser(response: RedirectResponse, provider: str, binding: str) -> RedirectResponse:
    # Issued by a top-level API navigation so cross-site frontend deployments do
    # not depend on third-party cookies. Providers return via top-level GET.
    response.set_cookie(cookie_name(provider), binding, max_age=STATE_TTL_SECONDS,
                        httponly=True, secure=get_settings().is_production, samesite="lax", path="/")
    return response


async def consume_state(request: Request, provider: str, state: str | None) -> str:
    binding = request.cookies.get(cookie_name(provider))
    if not state or len(state) > 200 or not binding or len(binding) > 200:
        raise HTTPException(400, "This sign-in expired or belongs to another browser. Start sign-in again.")
    try:
        async with _client() as client:
            origin = await client.eval(_CONSUME, 1, _key(provider, state), _digest(binding))
    except Exception as exc:
        raise HTTPException(503, "Sign-in verification is temporarily unavailable. Start sign-in again.") from exc
    if not origin:
        raise HTTPException(400, "This sign-in expired or was already used. Start sign-in again.")
    return origin
