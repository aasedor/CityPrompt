"""Short-lived OAuth codes, usable once with the initiating tab's PKCE proof."""

import base64
import hashlib
import json
import re
import secrets

from fastapi import HTTPException

from app.core.security import session_version
from app.services.oauth_state import _client, validate_challenge

EXCHANGE_TTL_SECONDS = 120
_CONSUME = """
local value = redis.call('GET', KEYS[1])
if not value then return false end
local record = cjson.decode(value)
if record.challenge ~= ARGV[1] or record.origin ~= ARGV[2] then return false end
redis.call('DEL', KEYS[1])
return value
"""


def _key(code: str) -> str:
    return "oauth-exchange:" + hashlib.sha256(code.encode()).hexdigest()


async def issue_exchange(user, origin: str, challenge: str) -> str:
    validate_challenge(challenge)
    code = secrets.token_urlsafe(32)
    record = {
        "user_id": str(user.id),
        "ver": session_version(user),
        "origin": origin,
        "challenge": challenge,
    }
    try:
        async with _client() as client:
            if not await client.set(_key(code), json.dumps(record), ex=EXCHANGE_TTL_SECONDS, nx=True):
                raise RuntimeError("Unable to issue sign-in code")
    except Exception:
        raise HTTPException(503, "Sign-in is temporarily unavailable. Start sign-in again.") from None
    return code


async def consume_exchange(code: str, verifier: str, origin: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", code) or not re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", verifier):
        raise HTTPException(400, "Invalid or expired sign-in code. Start sign-in again.")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    try:
        async with _client() as client:
            value = await client.eval(_CONSUME, 1, _key(code), challenge, origin)
    except Exception:
        raise HTTPException(503, "Sign-in verification is temporarily unavailable. Start sign-in again.") from None
    if not value:
        raise HTTPException(400, "Invalid or expired sign-in code. Start sign-in again.")
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        raise HTTPException(400, "Invalid sign-in code. Start sign-in again.") from None
