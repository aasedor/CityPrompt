"""Admission control must be atomic, bounded, and independent of untrusted headers."""

import asyncio
import os
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.core import rate_limit as limits


def request(peer="198.51.100.5", forwarded=None):
    headers = [] if forwarded is None else [(b"x-forwarded-for", forwarded.encode())]
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/login",
            "headers": headers,
            "scheme": "https",
            "server": ("test", 443),
            "client": (peer, 1234),
            "query_string": b"",
        }
    )


def test_spoofed_forwarded_header_is_ignored(monkeypatch):
    monkeypatch.setattr(limits, "get_settings", lambda: SimpleNamespace(trusted_proxy_cidrs=""))
    assert limits._get_client_ip(request(forwarded="1.1.1.1")) == "198.51.100.5"


def test_trusted_chain_uses_nearest_untrusted_hop(monkeypatch):
    monkeypatch.setattr(limits, "get_settings", lambda: SimpleNamespace(trusted_proxy_cidrs="10.0.0.0/8"))
    assert limits._get_client_ip(request("10.0.0.2", "1.1.1.1, 198.51.100.7, 10.0.0.1")) == "198.51.100.7"
    assert limits._get_client_ip(request("10.0.0.2", "garbage")) == "10.0.0.2"


@pytest.mark.asyncio
async def test_backend_failure_denies_admission(monkeypatch):
    monkeypatch.setattr(limits, "_get_redis", AsyncMock(side_effect=ConnectionError("private connection string")))
    with pytest.raises(HTTPException) as error:
        await limits.enforce_rate_limit(request(), 5)
    assert error.value.status_code == 503
    assert "private" not in error.value.detail


@pytest.mark.asyncio
async def test_atomic_script_parameters_and_no_personal_information_in_key(monkeypatch):
    store = AsyncMock()
    store.eval.return_value = [1, 0]
    monkeypatch.setattr(limits, "_get_redis", AsyncMock(return_value=store))
    await asyncio.gather(
        *(
            limits.enforce_rate_limit(request(), 5, bucket="login-email", identity="person@example.com")
            for _ in range(8)
        )
    )
    calls = store.eval.call_args_list
    assert len(calls) == 8
    assert len({c.args[-1] for c in calls}) == 8
    assert len({c.args[2] for c in calls}) == 1
    assert "person" not in calls[0].args[2] and "@" not in calls[0].args[2]
    assert "ZCARD" in calls[0].args[0] and "ZADD" in calls[0].args[0]


@pytest.mark.asyncio
async def test_exhausted_window_returns_retry_after(monkeypatch):
    store = AsyncMock()
    store.eval.return_value = [0, 17]
    monkeypatch.setattr(limits, "_get_redis", AsyncMock(return_value=store))
    with pytest.raises(HTTPException) as error:
        await limits.enforce_rate_limit(request(), 5)
    assert error.value.status_code == 429
    assert error.value.headers["Retry-After"] == "17"


@pytest.mark.asyncio
async def test_real_redis_atomic_admission_is_bounded(monkeypatch):
    """Opt-in uses a unique key and deletes only that key in a local test Redis."""
    from urllib.parse import urlsplit

    import redis.asyncio as redis

    url = os.getenv("CITYPROMPT_TEST_REDIS_URL")
    if not url:
        pytest.skip("Set CITYPROMPT_TEST_REDIS_URL for the real Lua concurrency check")
    assert urlsplit(url).hostname in {"localhost", "127.0.0.1", "::1"}
    store = redis.from_url(url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
    monkeypatch.setattr(limits, "_get_redis", AsyncMock(return_value=store))
    bucket = "test-admission-" + uuid.uuid4().hex
    import hashlib

    key = "rate_limit:v2:" + hashlib.sha256(f"{bucket}\0fixed".encode()).hexdigest()
    try:
        results = await asyncio.gather(
            *(limits.enforce_rate_limit(request(), 10, 60, bucket=bucket, identity="fixed") for _ in range(100)),
            return_exceptions=True,
        )
        assert sum(value is None for value in results) == 10
        assert sum(isinstance(value, HTTPException) and value.status_code == 429 for value in results) == 90
        assert await store.zcard(key) == 10
        assert 0 < await store.ttl(key) <= 60
    finally:
        await store.delete(key)
        await store.aclose()
