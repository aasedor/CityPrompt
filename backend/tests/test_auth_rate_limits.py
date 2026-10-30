"""Auth admission must run before credential, database and outbound email work."""

from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
import pytest

from app.api.v1 import auth
from app.core.security import create_refresh_token
from tests.conftest import FakeUser


def return_user(db, user):
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute = AsyncMock(return_value=result)


@pytest.mark.asyncio
async def test_login_account_limit_precedes_database_and_password_work(client, mock_db, monkeypatch):
    return_user(mock_db, None)
    verify = MagicMock(side_effect=AssertionError("No password hash should be checked for this synthetic missing user"))
    monkeypatch.setattr(auth, "verify_password", verify)
    for index in range(10):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "Student@example.com" if index % 2 else "student@example.com",
                "password": "wrong",
            },
        )
        assert response.status_code == 401
    before = mock_db.execute.await_count
    response = await client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": "wrong"})
    assert response.status_code == 429
    assert mock_db.execute.await_count == before
    verify.assert_not_called()


@pytest.mark.asyncio
async def test_registration_account_limit_precedes_hashing(client, mock_db, monkeypatch):
    return_user(mock_db, FakeUser())
    hashed = MagicMock(side_effect=AssertionError("Duplicate registrations must not hash"))
    monkeypatch.setattr(auth, "hash_password", hashed)
    for _ in range(3):
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "student@example.com", "password": "new-password"},
        )
        assert response.status_code == 409
    before = mock_db.execute.await_count
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "Student@example.com", "password": "new-password"},
    )
    assert response.status_code == 429
    assert mock_db.execute.await_count == before
    hashed.assert_not_called()


@pytest.mark.asyncio
async def test_reset_email_limit_precedes_outbound_email(client, mock_db, monkeypatch):
    return_user(mock_db, FakeUser())
    sent = AsyncMock()
    monkeypatch.setattr("app.core.email.send_password_reset_email", sent)
    for _ in range(3):
        response = await client.post("/api/v1/auth/forgot-password", json={"email": "student@example.com"})
        assert response.status_code == 200
    before = mock_db.execute.await_count
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "Student@example.com"})
    assert response.status_code == 429
    assert mock_db.execute.await_count == before
    assert sent.await_count == 3


@pytest.mark.asyncio
async def test_reset_attempt_limit_runs_before_token_decoding(client, mock_db, monkeypatch):
    decode_calls = []

    def invalid(_token):
        decode_calls.append(True)
        raise HTTPException(401, "Invalid token")

    monkeypatch.setattr(auth, "decode_token", invalid)
    for _ in range(30):
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid", "new_password": "new-password"},
        )
        assert response.status_code == 401
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid", "new_password": "new-password"},
    )
    assert response.status_code == 429
    assert len(decode_calls) == 30
    mock_db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_auth_admission_outage_fails_closed_before_database(client, mock_db, monkeypatch):
    return_user(mock_db, None)

    async def unavailable(*_args, **_kwargs):
        raise HTTPException(503, "Sign-in temporarily unavailable")

    monkeypatch.setattr(auth, "enforce_rate_limit", unavailable, raising=False)
    response = await client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": "wrong"})
    assert response.status_code == 503
    mock_db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_user_limit_precedes_database_work(client, mock_db):
    import uuid

    return_user(mock_db, None)
    token = create_refresh_token(str(uuid.uuid4()))
    for _ in range(60):
        response = await client.post("/api/v1/auth/refresh", json={"refresh_token": token})
        assert response.status_code == 401
    before = mock_db.execute.await_count
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert response.status_code == 429
    assert mock_db.execute.await_count == before


@pytest.mark.asyncio
async def test_rotating_untrusted_forwarding_headers_does_not_evade_auth_ip_limit(client, mock_db, monkeypatch):
    from types import SimpleNamespace
    from app.core import rate_limit

    monkeypatch.setattr(rate_limit, "get_settings", lambda: SimpleNamespace(trusted_proxy_cidrs=""))
    return_user(mock_db, None)
    for index in range(120):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": f"student{index}@example.com", "password": "wrong"},
            headers={"X-Forwarded-For": f"192.0.2.{index}"},
        )
        assert response.status_code == 401
    before = mock_db.execute.await_count
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "another@example.com", "password": "wrong"},
        headers={"X-Forwarded-For": "198.51.100.1"},
    )
    assert response.status_code == 429
    assert mock_db.execute.await_count == before
