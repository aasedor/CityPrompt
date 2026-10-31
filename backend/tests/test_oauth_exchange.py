"""OAuth callback transport: URL codes cannot mint sessions without browser proof."""

# Imported pytest fixtures are intentionally shadowed by injected parameters.
# ruff: noqa: F811

import asyncio
import base64
import hashlib
import json
import os
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException, Response
import pytest
import redis.asyncio as redis
from sqlalchemy import select
from starlette.requests import Request

from app.api.v1 import oauth
from app.core import security
from app.models.models import UserRefreshSession
from tests.test_auth_sessions import (
    local_db,  # noqa: F401
    local_user,  # noqa: F401
    provider_login,
    reset_link,
    auth_request,
)  # noqa: F401

VERIFIER = "b" * 43
CHALLENGE = base64.urlsafe_b64encode(hashlib.sha256(VERIFIER.encode()).digest()).decode().rstrip("=")
ORIGIN = "https://class.example"


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["google", "microsoft"])
async def test_callback_contains_code_and_never_issues_bearer_tokens(local_db, monkeypatch, provider):
    response = await provider_login(
        local_db,
        monkeypatch,
        provider,
        {
            "sub": "student-subject",
            "email": "student@gmail.com",
            "email_verified": True,
        },
    )
    parsed = urlparse(response.headers["location"])
    query = parse_qs(parsed.query)
    assert set(query) == {"code"}
    assert not parsed.fragment
    assert "access_token" not in response.headers["location"]
    assert "refresh_token" not in response.headers["location"]
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert local_db.session.execute(select(UserRefreshSession)).scalars().all() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["google", "microsoft"])
async def test_callback_commits_identity_before_publishing_code(local_db, monkeypatch, provider):
    committed = False

    async def commit():
        nonlocal committed
        local_db.session.commit()
        committed = True

    async def publish(_user, _origin, _challenge):
        assert committed, "A code must not escape before its user's transaction commits"
        return "x" * 43

    local_db.commit = commit
    response = await provider_login(
        local_db,
        monkeypatch,
        provider,
        {"sub": "student-subject", "email": "student@gmail.com", "email_verified": True},
        publish=publish,
    )
    assert response.status_code == 302


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["google", "microsoft"])
async def test_legacy_start_without_browser_proof_fails_closed(client, monkeypatch, provider):
    monkeypatch.setattr(oauth.settings, f"{provider}_client_id", "test-client")
    response = await client.get(f"/api/v1/auth/oauth/{provider}?frontend_origin={ORIGIN}")
    assert response.status_code == 400
    assert "sign-in" in response.json()["detail"].lower()


class ExchangeStore:
    """Only the external store is replaced; real Lua gets a separate Redis check."""

    def __init__(self):
        self.values = {}
        self.now = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        pass

    async def set(self, key, value, *, ex, nx):
        assert nx
        if key in self.values:
            return False
        self.values[key] = (value, self.now + ex)
        return True

    async def eval(self, _script, key_count, key, challenge, origin):
        assert key_count == 1
        item = self.values.get(key)
        if not item or item[1] <= self.now:
            return None
        record = json.loads(item[0])
        if record["challenge"] != challenge or record["origin"] != origin:
            return None
        del self.values[key]
        return item[0]


@pytest.fixture
def exchange_store(monkeypatch):
    from app.services import oauth_exchange

    store = ExchangeStore()
    monkeypatch.setattr(oauth_exchange, "_client", lambda: store)
    return store


def exchange_request(origin=ORIGIN):
    return Request(
        {
            "type": "http",
            "headers": [(b"origin", origin.encode())],
            "client": ("127.0.0.1", 1234),
        }
    )


@pytest.mark.asyncio
async def test_code_is_browser_bound_and_single_use(exchange_store, local_user):
    from app.services import oauth_exchange as broker

    code = await broker.issue_exchange(local_user, ORIGIN, CHALLENGE)
    for verifier, origin in [("c" * 43, ORIGIN), (VERIFIER, "https://other.example")]:
        with pytest.raises(HTTPException) as rejected:
            await broker.consume_exchange(code, verifier, origin)
        assert rejected.value.status_code == 400
    record = await broker.consume_exchange(code, VERIFIER, ORIGIN)
    assert record["user_id"] == str(local_user.id)
    assert record["ver"] == 0
    with pytest.raises(HTTPException):
        await broker.consume_exchange(code, VERIFIER, ORIGIN)


@pytest.mark.asyncio
async def test_code_expires_without_reaching_session_issuance(exchange_store, local_user):
    from app.services import oauth_exchange as broker

    code = await broker.issue_exchange(local_user, ORIGIN, CHALLENGE)
    exchange_store.now = 121
    with pytest.raises(HTTPException) as rejected:
        await broker.consume_exchange(code, VERIFIER, ORIGIN)
    assert rejected.value.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["active", "disabled", "recovered"])
async def test_exchange_rechecks_current_user_before_minting_tokens(
    exchange_store, local_db, local_user, monkeypatch, state
):
    from app.services import oauth_exchange as broker
    from app.core.config import get_settings

    monkeypatch.setattr(
        oauth,
        "settings",
        get_settings().model_copy(update={"frontend_url": ORIGIN, "cors_origins": [ORIGIN]}),
    )
    code = await broker.issue_exchange(local_user, ORIGIN, CHALLENGE)
    if state == "disabled":
        local_user.is_active = False
    elif state == "recovered":
        from app.api.v1 import auth
        from app.schemas.schemas import ResetPasswordRequest

        token = await reset_link(local_db, local_user, monkeypatch)
        await auth.reset_password(
            ResetPasswordRequest(token=token, new_password="recovered-password"),
            local_db,
            request=auth_request(),
        )
    await local_db.flush()
    body = oauth.OAuthExchangeRequest(code=code, code_verifier=VERIFIER)
    if state == "active":
        response = Response()
        result = await oauth.exchange_code(body, exchange_request(), response, local_db)
        assert response.headers["cache-control"] == "no-store"
        assert result.user.id == local_user.id
        assert (await security.get_current_user(result.access_token, local_db)).id == local_user.id
        assert len(local_db.session.execute(select(UserRefreshSession)).scalars().all()) == 1
    else:
        with pytest.raises(HTTPException) as rejected:
            await oauth.exchange_code(body, exchange_request(), Response(), local_db)
        assert rejected.value.status_code == 401
        assert local_db.session.execute(select(UserRefreshSession)).scalars().all() == []


@pytest.mark.asyncio
async def test_exchange_store_outage_fails_closed(monkeypatch, local_user):
    from app.services import oauth_exchange as broker

    store = AsyncMock()
    store.__aenter__.return_value = store
    store.set.side_effect = ConnectionError("offline")
    store.eval.side_effect = ConnectionError("offline")
    monkeypatch.setattr(broker, "_client", lambda: store)
    for operation in [
        broker.issue_exchange(local_user, ORIGIN, CHALLENGE),
        broker.consume_exchange("x" * 43, VERIFIER, ORIGIN),
    ]:
        with pytest.raises(HTTPException) as rejected:
            await operation
        assert rejected.value.status_code == 503


@pytest.mark.asyncio
async def test_real_redis_exchange_has_one_winner_and_invalid_proof_does_not_consume(monkeypatch, local_user):
    from app.services import oauth_exchange as broker

    url = os.getenv("CITYPROMPT_TEST_REDIS_URL")
    if not url:
        pytest.skip("Set CITYPROMPT_TEST_REDIS_URL for isolated-key exchange Lua verification")
    monkeypatch.setattr(broker, "_client", lambda: redis.from_url(url, decode_responses=True))
    code = await broker.issue_exchange(local_user, ORIGIN, CHALLENGE)
    async with redis.from_url(url, decode_responses=True) as store:
        try:
            assert 0 < await store.ttl(broker._key(code)) <= 120
            with pytest.raises(HTTPException):
                await broker.consume_exchange(code, "c" * 43, ORIGIN)
            with pytest.raises(HTTPException):
                await broker.consume_exchange(code, VERIFIER, "https://wrong.example")
            results = await asyncio.gather(
                *(broker.consume_exchange(code, VERIFIER, ORIGIN) for _ in range(12)),
                return_exceptions=True,
            )
            assert sum(isinstance(result, dict) for result in results) == 1
            assert sum(isinstance(result, HTTPException) and result.status_code == 400 for result in results) == 11
            expired = await broker.issue_exchange(local_user, ORIGIN, CHALLENGE)
            await store.expire(broker._key(expired), 0)
            with pytest.raises(HTTPException):
                await broker.consume_exchange(expired, VERIFIER, ORIGIN)
        finally:
            await store.delete(broker._key(code))


@pytest.mark.asyncio
@pytest.mark.parametrize("verifier,status", [(VERIFIER, 400), ("v" * 42 + "=", 422)])
async def test_exchange_errors_are_noncacheable_and_do_not_echo_proof(client, verifier, status):
    response = await client.post(
        "/api/v1/auth/oauth/exchange",
        json={"code": "x" * 43, "code_verifier": verifier},
    )
    assert response.status_code == status
    assert response.headers["cache-control"] == "no-store"
    assert verifier not in response.text
