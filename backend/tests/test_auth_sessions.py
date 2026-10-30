"""Authentication boundaries with real SQL and synthetic users/providers only."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.api.v1 import auth, oauth
from app.core import security
from app.models.models import User
from app.schemas.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    UserCreate,
)


def auth_request():
    return Request(
        {
            "type": "http",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "path": "/auth-test",
        }
    )


class LocalSession:
    """Run production SQL in disposable SQLite; PostgreSQL races are tested separately."""

    def __init__(self, session):
        self.session = session

    async def execute(self, query):
        return self.session.execute(query)

    async def flush(self):
        self.session.flush()

    async def refresh(self, value):
        self.session.refresh(value)

    def add(self, value):
        self.session.add(value)


@pytest.fixture
def local_db():
    engine = create_engine("sqlite://")
    User.__table__.create(engine)
    # The rotation table is created when introduced by the production fix.
    table = User.metadata.tables.get("user_refresh_sessions")
    if table is not None:
        table.create(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield LocalSession(session)
    engine.dispose()


@pytest.fixture
def local_user(local_db):
    user = User(
        email="student@gmail.com",
        hashed_password=security.hash_password("old-password"),
    )
    local_db.add(user)
    local_db.session.flush()
    return user


async def sign_in(db, user):
    return await auth.login(
        LoginRequest(email=user.email, password="old-password"),
        db,
        request=auth_request(),
    )


async def reset_link(db, user, monkeypatch):
    sent = AsyncMock()
    monkeypatch.setattr("app.core.email.send_password_reset_email", sent)
    await auth.forgot_password(ForgotPasswordRequest(email=user.email), db, request=auth_request())
    link = sent.await_args.args[1]
    return parse_qs(urlparse(link).query)["token"][0]


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["access", "refresh"])
async def test_password_change_rejects_all_prechange_tokens(local_db, local_user, kind):
    tokens = await sign_in(local_db, local_user)
    await auth.change_password(
        ChangePasswordRequest(current_password="old-password", new_password="new-password"),
        local_user,
        local_db,
        request=auth_request(),
    )
    with pytest.raises(HTTPException) as rejected:
        if kind == "access":
            await security.get_current_user(tokens.access_token, local_db)
        else:
            await auth.refresh_token(
                RefreshRequest(refresh_token=tokens.refresh_token),
                local_db,
                request=auth_request(),
            )
    assert rejected.value.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["access", "refresh"])
async def test_password_reset_rejects_all_previous_tokens(local_db, local_user, monkeypatch, kind):
    tokens = await sign_in(local_db, local_user)
    token = await reset_link(local_db, local_user, monkeypatch)
    await auth.reset_password(
        ResetPasswordRequest(token=token, new_password="recovered-password"),
        local_db,
        request=auth_request(),
    )
    with pytest.raises(HTTPException) as rejected:
        if kind == "access":
            await security.get_current_user(tokens.access_token, local_db)
        else:
            await auth.refresh_token(
                RefreshRequest(refresh_token=tokens.refresh_token),
                local_db,
                request=auth_request(),
            )
    assert rejected.value.status_code == 401


@pytest.mark.asyncio
async def test_password_reset_link_is_single_use(local_db, local_user, monkeypatch):
    token = await reset_link(local_db, local_user, monkeypatch)
    await auth.reset_password(
        ResetPasswordRequest(token=token, new_password="recovered-password"),
        local_db,
        request=auth_request(),
    )
    with pytest.raises(HTTPException) as rejected:
        await auth.reset_password(
            ResetPasswordRequest(token=token, new_password="replayed-password"),
            local_db,
            request=auth_request(),
        )
    assert rejected.value.status_code in (400, 401)
    assert security.verify_password("recovered-password", local_user.hashed_password)


@pytest.mark.asyncio
async def test_new_reset_request_invalidates_previous_link(local_db, local_user, monkeypatch):
    old = await reset_link(local_db, local_user, monkeypatch)
    new = await reset_link(local_db, local_user, monkeypatch)
    with pytest.raises(HTTPException):
        await auth.reset_password(
            ResetPasswordRequest(token=old, new_password="replayed-password"),
            local_db,
            request=auth_request(),
        )
    await auth.reset_password(
        ResetPasswordRequest(token=new, new_password="recovered-password"),
        local_db,
        request=auth_request(),
    )


@pytest.mark.asyncio
async def test_refresh_token_rotates_and_replay_is_denied(local_db, local_user):
    first = await sign_in(local_db, local_user)
    second = await auth.refresh_token(
        RefreshRequest(refresh_token=first.refresh_token),
        local_db,
        request=auth_request(),
    )
    assert second.refresh_token != first.refresh_token
    with pytest.raises(HTTPException) as rejected:
        await auth.refresh_token(
            RefreshRequest(refresh_token=first.refresh_token),
            local_db,
            request=auth_request(),
        )
    assert rejected.value.status_code == 401
    third = await auth.refresh_token(
        RefreshRequest(refresh_token=second.refresh_token),
        local_db,
        request=auth_request(),
    )
    assert (await security.get_current_user(third.access_token, local_db)).id == local_user.id


@pytest.mark.asyncio
async def test_independent_signins_keep_independent_refresh_sessions(local_db, local_user):
    first = await sign_in(local_db, local_user)
    second = await sign_in(local_db, local_user)
    assert first.refresh_token != second.refresh_token
    for tokens in (first, second):
        rotated = await auth.refresh_token(
            RefreshRequest(refresh_token=tokens.refresh_token),
            local_db,
            request=auth_request(),
        )
        assert rotated.user.id == local_user.id


@pytest.mark.asyncio
async def test_legacy_unversioned_bearer_is_rejected(local_db, local_user):
    token = jwt.encode(
        {
            "sub": str(local_user.id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
        },
        security.settings.jwt_secret_key,
        algorithm=security.settings.jwt_algorithm,
    )
    with pytest.raises(HTTPException) as rejected:
        await security.get_current_user(token, local_db)
    assert rejected.value.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("route", ["access", "refresh", "reset"])
async def test_malformed_signed_subject_returns_auth_error(local_db, route):
    token = jwt.encode(
        {
            "sub": "not-a-uuid",
            "type": route,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
        },
        security.settings.jwt_secret_key,
        algorithm=security.settings.jwt_algorithm,
    )
    with pytest.raises(HTTPException) as rejected:
        if route == "access":
            await security.get_current_user(token, local_db)
        elif route == "refresh":
            await auth.refresh_token(RefreshRequest(refresh_token=token), local_db, request=auth_request())
        else:
            await auth.reset_password(
                ResetPasswordRequest(token=token, new_password="new-password"),
                local_db,
                request=auth_request(),
            )
    assert rejected.value.status_code in (400, 401)


async def provider_login(db, monkeypatch, provider, profile):
    monkeypatch.setattr(
        oauth,
        "settings",
        SimpleNamespace(
            google_client_id="fake",
            google_client_secret="fake",
            google_redirect_uri="https://api.example/callback",
            microsoft_client_id="fake",
            microsoft_client_secret="fake",
            microsoft_redirect_uri="https://api.example/callback",
        ),
    )
    monkeypatch.setattr(oauth, "consume_state", AsyncMock(return_value="https://class.example"))
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.post.return_value = SimpleNamespace(status_code=200, json=lambda: {"access_token": "mock-provider-token"})
    client.get.return_value = SimpleNamespace(status_code=200, json=lambda: profile)
    monkeypatch.setattr(oauth.httpx, "AsyncClient", lambda: client)
    request = Request({"type": "http", "headers": []})
    return await getattr(oauth, f"{provider}_callback")(request, code="mock-code", state="mock-state", db=db)


@pytest.mark.asyncio
async def test_authoritative_google_binding_removes_preregistered_password_and_sessions(
    local_db, local_user, monkeypatch
):
    prior = await sign_in(local_db, local_user)
    response = await provider_login(
        local_db,
        monkeypatch,
        "google",
        {
            "sub": "google-student",
            "id": "google-student",
            "email": local_user.email,
            "email_verified": True,
            "verified_email": True,
        },
    )
    assert "oauth_error" not in response.headers["location"]
    assert local_user.hashed_password is None
    assert local_user.oauth_subject == "google-student"
    for kind in ("password", "access", "refresh"):
        with pytest.raises(HTTPException):
            if kind == "password":
                await sign_in(local_db, local_user)
            elif kind == "access":
                await security.get_current_user(prior.access_token, local_db)
            else:
                await auth.refresh_token(
                    RefreshRequest(refresh_token=prior.refresh_token),
                    local_db,
                    request=auth_request(),
                )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider,profile",
    [
        (
            "google",
            {
                "sub": "foreign",
                "id": "foreign",
                "email": "student@gmail.com",
                "email_verified": False,
                "verified_email": False,
            },
        ),
        (
            "google",
            {
                "sub": "foreign",
                "id": "foreign",
                "email": "student@example.com",
                "email_verified": True,
                "verified_email": True,
            },
        ),
        (
            "microsoft",
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "sub": "ms-student",
                "mail": "student@gmail.com",
                "userPrincipalName": "student@gmail.com",
                "email": "student@gmail.com",
            },
        ),
    ],
)
async def test_nonauthoritative_email_never_merges_existing_account(
    local_db, local_user, monkeypatch, provider, profile
):
    local_user.email = profile.get("email")
    await local_db.flush()
    old_hash = local_user.hashed_password
    response = await provider_login(local_db, monkeypatch, provider, profile)
    assert "oauth_error" in response.headers["location"]
    assert local_user.hashed_password == old_hash
    assert local_user.oauth_provider is None


@pytest.mark.asyncio
async def test_provider_subject_controls_returning_login_even_after_email_changes(local_db, local_user, monkeypatch):
    local_user.oauth_provider = "google"
    local_user.oauth_subject = "google-student"
    local_user.hashed_password = None
    await local_db.flush()
    response = await provider_login(
        local_db,
        monkeypatch,
        "google",
        {
            "sub": "google-student",
            "id": "google-student",
            "email": "new@gmail.com",
            "email_verified": True,
            "verified_email": True,
        },
    )
    assert "oauth_error" not in response.headers["location"]
    users = local_db.session.execute(select(User)).scalars().all()
    assert len(users) == 1
    assert users[0].id == local_user.id


@pytest.mark.asyncio
async def test_same_email_different_subject_cannot_replace_bound_identity(local_db, local_user, monkeypatch):
    local_user.oauth_provider = "google"
    local_user.oauth_subject = "original-subject"
    await local_db.flush()
    response = await provider_login(
        local_db,
        monkeypatch,
        "google",
        {
            "sub": "other-subject",
            "id": "other-subject",
            "email": local_user.email,
            "email_verified": True,
            "verified_email": True,
        },
    )
    assert "oauth_error" in response.headers["location"]
    assert local_user.oauth_subject == "original-subject"


@pytest.mark.asyncio
async def test_disabled_oauth_account_is_not_modified(local_db, local_user, monkeypatch):
    local_user.is_active = False
    await local_db.flush()
    old_hash = local_user.hashed_password
    response = await provider_login(
        local_db,
        monkeypatch,
        "google",
        {
            "sub": "google-student",
            "id": "google-student",
            "email": local_user.email,
            "email_verified": True,
            "verified_email": True,
        },
    )
    assert "oauth_error" in response.headers["location"]
    assert local_user.oauth_provider is None
    assert local_user.hashed_password == old_hash


@pytest.mark.asyncio
async def test_case_insensitive_registration_refuses_an_existing_email(local_db, local_user):
    with pytest.raises(HTTPException) as rejected:
        await auth.register(
            UserCreate(email="Student@gmail.com", password="new-password"),
            local_db,
            request=auth_request(),
        )
    assert rejected.value.status_code == 409


@pytest.mark.asyncio
async def test_legacy_duplicate_email_login_fails_closed(local_db, local_user):
    local_db.add(
        User(
            email="STUDENT@gmail.com",
            hashed_password=security.hash_password("old-password"),
        )
    )
    await local_db.flush()
    with pytest.raises(HTTPException) as rejected:
        await sign_in(local_db, local_user)
    assert rejected.value.status_code in (401, 409)


@pytest.mark.asyncio
async def test_password_change_invalidates_an_already_issued_reset(local_db, local_user, monkeypatch):
    token = await reset_link(local_db, local_user, monkeypatch)
    await auth.change_password(
        ChangePasswordRequest(current_password="old-password", new_password="new-password"),
        local_user,
        local_db,
        request=auth_request(),
    )
    with pytest.raises(HTTPException):
        await auth.reset_password(
            ResetPasswordRequest(token=token, new_password="replayed-password"),
            local_db,
            request=auth_request(),
        )
    assert security.verify_password("new-password", local_user.hashed_password)


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["google", "microsoft"])
async def test_new_provider_account_binds_subject_and_never_switches_users(local_db, monkeypatch, provider):
    profile = {
        "sub": "new-student-subject",
        "email": "new@gmail.com",
        "email_verified": True,
    }
    response = await provider_login(local_db, monkeypatch, provider, profile)
    assert "oauth_error" not in response.headers["location"]
    user = local_db.session.execute(select(User)).scalar_one()
    assert user.oauth_subject == "new-student-subject" and user.hashed_password is None
    assert user.render_credits == 1000 and user.role == "editor"
    response = await provider_login(local_db, monkeypatch, provider, {"sub": "new-student-subject"})
    assert "oauth_error" not in response.headers["location"]
    assert local_db.session.execute(select(User)).scalar_one().id == user.id
    user.is_active = False
    await local_db.flush()
    response = await provider_login(local_db, monkeypatch, provider, profile)
    assert "oauth_error" in response.headers["location"]


@pytest.mark.asyncio
async def test_legacy_microsoft_email_is_not_identity_proof(local_db, local_user, monkeypatch):
    local_user.oauth_provider = "microsoft"
    local_user.hashed_password = None
    await local_db.flush()
    response = await provider_login(
        local_db,
        monkeypatch,
        "microsoft",
        {"sub": "unbound-subject", "email": local_user.email},
    )
    assert "oauth_error" in response.headers["location"]
    assert local_user.oauth_subject is None


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["microsoft", "google"])
async def test_mailbox_recovery_severs_untrusted_provider_identity(local_db, monkeypatch, provider):
    # Provider email may be controlled by a tenant admin or be an outdated
    # third-party Google address. It is not current mailbox ownership proof.
    profile = {
        "sub": "prior-untrusted-subject",
        "email": "student@example.com",
        "email_verified": True,
    }
    response = await provider_login(local_db, monkeypatch, provider, profile)
    assert "oauth_error" not in response.headers["location"]
    user = local_db.session.execute(select(User)).scalar_one()
    token = await reset_link(local_db, user, monkeypatch)
    await auth.reset_password(
        ResetPasswordRequest(token=token, new_password="mailbox-owner-password"),
        local_db,
        request=auth_request(),
    )
    recovered = await auth.login(
        LoginRequest(email=user.email, password="mailbox-owner-password"),
        local_db,
        request=auth_request(),
    )
    assert recovered.user.id == user.id
    response = await provider_login(local_db, monkeypatch, provider, profile)
    assert "oauth_error" in response.headers["location"]
    assert user.oauth_subject is None
    assert user.oauth_provider is None
    assert security.verify_password("mailbox-owner-password", user.hashed_password)
